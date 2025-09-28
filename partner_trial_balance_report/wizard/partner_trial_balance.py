from odoo import models, fields, api


class PartnerTrialBalance(models.TransientModel):
    _name = 'partner.trial.balance'
    _description = 'Partner Trial Balance Report'

    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    result_selection = fields.Selection([('customer', 'Receivable Accounts'),
                                         ('supplier', 'Payable Accounts'),
                                         ], string="Partner's", required=True, default='customer')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    is_balance = fields.Boolean("Zero Balance")

    def action_print_report(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'partner_id': self.partner_id.id or False,
            'selection': self.result_selection,
            'company': self.company_id.id,
            'is_balance': self.is_balance,
        }
        return self.env.ref('partner_trial_balance_report.action_partner_trial').report_action(self, data=data)
