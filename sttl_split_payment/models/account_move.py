from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_split_payment(self):
        # Ensure self contains `account.move` records
        if not self:
            return

        if not self.check_same_partner():
            raise ValidationError("Split Payment is only allowed for invoices with the same partner.")

        if not self.check_for_posted():
            raise ValidationError("You can only register payment for posted journal entries.")
        if not self.check_for_paid():
            raise ValidationError("You can't register a payment because there is nothing left to pay on the selected "
                                  "journal items.")

        move_types = self.mapped('move_type')
        print(move_types)
        if all(move_type == 'in_invoice' for move_type in move_types):
            payment_type = 'send'
        elif all(move_type == 'out_invoice' for move_type in move_types):
            payment_type = 'receive'
        else:
            raise ValidationError("Split Payment is only allowed for bills or invoices, not a mix of both.")

        # Create the `invoice.reconcile` record
        invoice_reconcile = self.env['invoice.reconcile'].create({
            'partner_id': self[0].partner_id.id,  # Use the partner of the first invoice
            'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
            'payment_type': payment_type,
            'amount': 0,  # Total amount from the invoices
            'date': fields.Date.today(),
            'state': 'draft',
        })

        split_payment_lines = []
        for move in self:
            split_payment_line = self.env['split.payment.line'].create({
                'invoice_reconcile_id': invoice_reconcile.id,
                'invoice_id': move.id,
                'amount_by_user': 0,  # Set the amount for each invoice
            })
            split_payment_lines.append(split_payment_line.id)

        invoice_reconcile.write({
            'invoice_ids': [(6, 0, split_payment_lines)]  # Link the created split payment lines
        })
        return {
            'name': 'Invoice Reconcile',
            'view_mode': 'form',
            'res_model': 'invoice.reconcile',
            'res_id': invoice_reconcile.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def check_same_partner(self):
        partners = set()
        for invoice in self:
            partners.add(invoice.partner_id)
        if len(partners) > 1:
            return False
        return True

    def check_for_posted(self):
        for invoice in self:
            if invoice.state != 'posted':
                return False
        return True

    def check_for_paid(self):
        for invoice in self:
            if invoice.payment_state == 'paid':
                return False
        return True
