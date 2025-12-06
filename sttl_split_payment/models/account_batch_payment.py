from odoo import fields, models, api


class AccountBatchPayment(models.Model):
    _inherit = "account.batch.payment"

    invoice_reconcile_id = fields.Many2one('invoice.reconcile')
