from odoo import fields, models, api
from odoo.exceptions import ValidationError


class CustomInvoiceLine(models.Model):
    _name = "split.payment.line"

    invoice_reconcile_id = fields.Many2one('invoice.reconcile')
    invoice_id = fields.Many2one('account.move')
    name = fields.Char(related="invoice_id.name", store=True)
    partner_id = fields.Many2one(related="invoice_id.partner_id", store=True)
    amount_residual = fields.Monetary(compute="_compute_amount_residual", currency_field='currency_id', store=True)
    amount_by_user = fields.Monetary('Amount', currency_field='currency_id')
    amount_by_user_percentage = fields.Float('Percentage')
    currency_id = fields.Many2one(related="invoice_id.currency_id", store=True)
    state = fields.Selection(related="invoice_id.state", store=True)
    move_type = fields.Selection(related="invoice_id.move_type", store=True)
    payment_state = fields.Selection(related="invoice_id.payment_state", store=True)
    invoice_partner_display_name = fields.Char(related="invoice_id.invoice_partner_display_name", store=True)
    company_id = fields.Many2one(related="invoice_id.company_id", store=True)
    invoice_total = fields.Monetary(related="invoice_id.amount_total_signed", store=True)

    # Compute fields
    parent_partner_id = fields.Many2one(related='invoice_reconcile_id.partner_id', store=True)
    payment_type = fields.Selection(related='invoice_reconcile_id.payment_type',store=True)

    @api.constrains('invoice_id')
    def _check_duplicate_value(self):
        for line in self:
            duplicates = self.search([
                ('invoice_id', '=', line.invoice_id.id),
                ('id', '!=', line.id),
                ('invoice_reconcile_id', '=', line.invoice_reconcile_id.id)
            ])
            if duplicates:
                raise ValidationError(f"The value for invoice '{line.name}' is selected multiple times.")

    @api.depends('invoice_id')
    def _compute_amount_residual(self):
        for line in self:
            line.amount_residual = line.invoice_id.amount_residual

    @api.onchange('amount_by_user_percentage')
    def _onchange_amount_by_user_percentage(self):
        for line in self:
            if line.amount_by_user_percentage:
                # Calculate amount_by_user based on percentage
                line.amount_by_user = (line.amount_by_user_percentage / 100) * line.amount_residual

    @api.onchange('amount_by_user')
    def _onchange_amount_by_user(self):
        for line in self:
            if line.amount_by_user and line.amount_residual:
                # Calculate percentage based on amount_by_user
                line.amount_by_user_percentage = (line.amount_by_user / line.amount_residual) * 100
