from odoo import fields, models, api
from odoo.exceptions import UserError


class RemainingPayment(models.TransientModel):
    _name = "payment.remaining"
    record_id = fields.Many2one('invoice.reconcile', string="Record")
    amount = fields.Float(string="Remaining Amount")
    message = fields.Text(string="Message", default="Do you want to create payment for the remaining amount?")

    def action_yes(self):
        # Create payment for the remaining amount
        if not self.record_id:
            raise UserError("Record not found.")

        # Create payment logic (adapt as necessary for your use case)
        payment_vals = {
            'amount': self.amount,
            'partner_id': self.record_id.partner_id.id,
        }
        payment = self.env['account.payment'].create(payment_vals)
        payment.action_post()

        # Continue with action_confirm
        return self.record_id.with_context(skip_popup=True).action_confirm()

    def action_no(self):
        return {'type': 'ir.actions.act_window_close'}
