from odoo import models, api

class ResPartner(models.Model):
    _inherit = "res.partner"

    def action_open_customer_ledger(self):
        """
        Opens the ledger report when the action is selected.
        """
        return self.env.ref('customer_partner_ledger.customer_ledger_report').report_action(self)
