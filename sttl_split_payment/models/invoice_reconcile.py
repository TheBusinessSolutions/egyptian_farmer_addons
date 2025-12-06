from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    invoice_reconcile_id = fields.Many2one('invoice.reconcile')
    is_split_payment = fields.Selection([
        ('partial', 'Partial')
    ])


class InvoiceReconcile(models.Model):
    _name = 'invoice.reconcile'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # field declaration:
    name = fields.Char("Split Payment Number", default="Draft")
    partner_id = fields.Many2one('res.partner', 'Customer/Vendor',
                                 domain="['|', ('parent_id','=', False), ('is_company','=', True)]", )
    journal_id = fields.Many2one('account.journal', 'Journal', domain=[('type', 'in', ['bank', 'cash'])],
                                 default=lambda self: self.env['account.journal'].search([('type', '=', 'bank')],
                                                                                         limit=1))
    payment_method_line_id = fields.Many2one('account.payment.method.line', string='Payment Method',
                                             domain="[('id', 'in', available_payment_method_line_ids)]",
                                             compute="_compute_payment_method_id",
                                             readonly=False, store=True, copy=False)
    partner_bank_id = fields.Many2one('res.partner.bank', string="Recipient Bank Account",
                                      readonly=False, store=True, tracking=True)
    payment_type = fields.Selection([
        ('send', 'Send'),
        ('receive', 'Receive')
    ], default="receive")
    invoice_count = fields.Integer('Invoice Count', compute='_compute_invoice_count', default=0)
    amount = fields.Monetary(currency_field='currency_id')
    date = fields.Date('Date', default=fields.Date.today)
    invoice_ids = fields.One2many('split.payment.line', 'invoice_reconcile_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('cancel', 'Cancel'),
    ], default='draft')
    available_payment_method_line_ids = fields.Many2many('account.payment.method.line',
                                                         compute='_compute_payment_method_line_fields')
    total_amount_by_user = fields.Monetary(
        string="Total Amount by User",
        compute="_compute_total_amount_by_user",
        store=True,
        currency_field='currency_id'
    )
    is_equal_distribution = fields.Boolean('Distribute Amount', store=True)
    remaining_amount = fields.Monetary(currency_field='currency_id', string='Remaining amount',
                                       compute="_compute_remaining_amount")
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        compute='_compute_currency_id', store=True, readonly=False, precompute=True,
        help="The payment's currency.")

    selected_invoice_ids = fields.Many2many('account.move')

    @api.onchange('amount', 'total_amount_by_user')
    def _compute_remaining_amount(self):
        for record in self:
            record.remaining_amount = record.amount - record.total_amount_by_user

    @api.onchange('amount')
    def _compute_amount(self):
        if self.amount < 0:
            raise ValidationError("The amount cannot be negative. Please enter a valid amount.")

    @api.onchange('partner_id')
    def _compute_invoice_lines(self):
        self.invoice_ids = False

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        for record in self:
            record.invoice_ids = False

    @api.onchange('is_equal_distribution')
    def _onchange_equal_distribution(self):
        for record in self:
            if record.is_equal_distribution:
                count = len(record.invoice_ids)
                for invoice in record.invoice_ids:
                    invoice.amount_by_user = record.amount / count
                    invoice.amount_by_user_percentage = (invoice.amount_by_user * 100) / invoice.amount_residual

    @api.onchange('amount')
    def _onchange_amount(self):
        for record in self:
            if record.is_equal_distribution:
                count = len(record.invoice_ids)
                for invoice in record.invoice_ids:
                    invoice.amount_by_user = record.amount / count
                    invoice.amount_by_user_percentage = (invoice.amount_by_user * 100) / invoice.amount_residual

    @api.onchange('invoice_ids')
    def _onchange_invoice_ids(self):
        for record in self:
            if record.is_equal_distribution:
                count = len(record.invoice_ids)
                for invoice in record.invoice_ids:
                    invoice.amount_by_user = record.amount / count
                    invoice.amount_by_user_percentage = (invoice.amount_by_user * 100) / invoice.amount_residual

    # Override create method
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('invoice.reconcile') or 'New'
        record = super(InvoiceReconcile, self).create(vals)
        if record.invoice_ids:
            record.check_partners()
        return record

    def write(self, vals):
        print(vals)
        res = super(InvoiceReconcile, self).write(vals)
        if self.invoice_ids and 'state' in vals and vals['state'] and vals['state'] == 'cancel':
            return res
        else:
            self.check_partners()
            return res

    def _compute_invoice_count(self):
        for reconcile in self:
            reconcile.invoice_count = len(reconcile.invoice_ids)

    def action_get_invoices(self):
        invoices = self.invoice_ids.invoice_id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', invoices.ids)],
        }

    def check_partners(self):
        for record in self:
            if record.invoice_ids:
                for invoice in record.invoice_ids:
                    if not invoice.partner_id or not record.partner_id:
                        raise UserError(
                            "Validation Error: Partner is missing on either the invoice or the split payment record."
                        )
                    if record.partner_id != invoice.partner_id:
                        raise UserError(
                            f"Validation Error: All selected invoices must belong to the same partner. "
                            f"Mismatch found with invoice {invoice.name}."
                        )
        return True

    # Validation function
    def _validate_amount_match(self):
        for record in self:
            if self.env.context.get('skip_popup'):
                # Skip validation logic when the popup is already handled
                return

            if record.amount != record.total_amount_by_user and record.amount < record.total_amount_by_user:
                raise ValidationError(
                    "The total amount must equal the sum of the user amounts on the invoices."
                )
            elif record.amount != record.total_amount_by_user and record.amount > record.total_amount_by_user:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Confirmation',
                    'res_model': 'payment.remaining',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_record_id': record.id,
                        'default_amount': record.amount - record.total_amount_by_user,
                    },
                }

    # methods
    @api.depends('invoice_ids.amount_by_user')
    def _compute_total_amount_by_user(self):
        for record in self:
            record.total_amount_by_user = sum(record.invoice_ids.mapped('amount_by_user'))

    @api.depends('journal_id')
    def _compute_currency_id(self):
        for pay in self:
            pay.currency_id = pay.journal_id.currency_id or pay.journal_id.company_id.currency_id

    def check_exceed_split(self):
        for inv in self:
            for invoice in inv.invoice_ids:
                if invoice.amount_by_user_percentage > 100:
                    raise ValidationError(
                        f"The split amount for {invoice.name or 'unknown'} exceeds actual remaining amount."
                        f" Please correct it."
                    )

    def action_confirm(self):
        self.check_exceed_split()
        action = self._validate_amount_match()
        if action:
            return action  # Return popup if condition is met

        for record in self:
            for invoice in record.invoice_ids:
                currency = invoice.company_id.currency_id if invoice.company_id else record.journal_id.currency_id or record.env.company.currency_id

                if not record.payment_method_line_id:
                    raise UserError("No payment method line found for the selected journal.")

                # Determine the correct payment type based on the invoice
                payment_type = 'inbound' if invoice.move_type == 'out_invoice' else 'outbound'

                wizard_vals = {
                    'journal_id': record.journal_id.id,
                    'require_partner_bank_account': False,
                    'payment_method_line_id': record.payment_method_line_id.id,
                    'group_payment': False,
                    'currency_id': currency.id,
                    'amount': invoice.amount_by_user,
                    'payment_date': record.date,
                    'communication': invoice.name,
                    'payment_type': payment_type,  # Set the correct payment type
                }

                wizard = self.env['account.payment.register'].with_context(
                    active_model='account.move',
                    active_ids=[invoice.invoice_id.id],
                    active_id=invoice.invoice_id.id
                ).create(wizard_vals)

                actions = wizard.action_create_payments()
                payment_ids = self.env['account.payment'].browse(actions.get('res_id'))
                for payment in payment_ids:
                    payment.is_split_payment = 'partial'
                    payment.invoice_reconcile_id = record.id

        batch = self.create_batch_payment_partial()
        batch.validate_batch_button()

        self.state = 'confirm'

    def create_batch_payment_partial(self):
        payment_ids = self.env['account.payment'].search([
            ('invoice_reconcile_id', '=', self.id)
        ])
        payment_method_id = payment_ids.payment_method_id.id
        payment_ids = payment_ids.ids

        batch_type = 'outbound' if self.payment_type == 'send' else 'inbound'
        print(batch_type)
        batch = self.env['account.batch.payment'].create({
            'journal_id': self.journal_id.id,
            'payment_ids': [(6, 0, payment_ids)],
            'payment_method_id': payment_method_id,
            'batch_type': batch_type,  # Set batch type dynamically
            'invoice_reconcile_id': self.id
        })
        return batch

    def action_cancel(self):
        for record in self:
            payments = self.env['account.payment'].search([('invoice_reconcile_id', '=', record.id)])
            if payments:
                for payment in payments:
                    if payment.reconciled_statement_lines_count != 0:
                        raise UserError('Payment related to this Split is already validated.')
                    else:
                        payment.action_cancel()
        self.state = 'cancel'

    def action_reset_to_draft(self):
        for record in self:
            payments = self.env['account.payment'].search([('invoice_reconcile_id', '=', record.id)])
            if payments:
                for payment in payments:
                    payment.action_draft()
        self.state = 'draft'

    def unlink(self):
        self.action_cancel()
        return super().unlink()

    # base methods
    @api.depends('payment_type', 'journal_id')
    def _compute_payment_method_line_fields(self):
        for pay in self:
            pay.available_payment_method_line_ids = pay.journal_id._get_available_payment_method_lines(pay.payment_type)
            to_exclude = pay._get_payment_method_codes_to_exclude()
            if to_exclude:
                pay.available_payment_method_line_ids = pay.available_payment_method_line_ids.filtered(
                    lambda x: x.code not in to_exclude)

    def _get_payment_method_codes_to_exclude(self):
        # Can be overridden to exclude payment methods based on the payment characteristics
        self.ensure_one()
        return []

    @api.depends('available_payment_method_line_ids')
    def _compute_payment_method_id(self):
        for record in self:
            available_payment_method_lines = record.available_payment_method_line_ids
            if record.payment_method_line_id in available_payment_method_lines:
                record.payment_method_line_id = record.payment_method_line_id
            elif available_payment_method_lines:
                record.payment_method_line_id = available_payment_method_lines[0]._origin
            else:
                record.payment_method_line_id = False
