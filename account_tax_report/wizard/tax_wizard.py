# -*- coding: utf-8 -*-
#from openerp import api, models, fields, _
from odoo import api, models, fields, _


class TaxReportWizard(models.TransientModel):
    _name = "tax.report.wizard"
    _description = 'Tax Report Wizard'
    
    @api.model
    def _get_tax_report(self):
        reports = []
        if self._context.get('active_id'):
            menu = self.env['ir.ui.menu'].browse(self._context.get('active_id')).name
            reports = self.env['taxes.report'].search([('name', 'ilike', menu)])
        return reports and reports[0] or False
    
    tax_report_id = fields.Many2one('taxes.report', string='Tax Reports', required=True, default=_get_tax_report)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id)
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries'),
                                    ], string='Target Moves', required=True, default='posted')

    display_detail = fields.Boolean('Display Detail', help='Display taxes with details.')

    
    def _build_comparison_context(self, data):
        result = {}
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        result['date_from'] = data['form']['date_from']
        result['date_to'] = data['form']['date_to']
        result['strict_range'] = True
        return result

#    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['tax_report_id', 'date_from', 'date_to', 'target_move', 'display_detail'])[0]
        for field in ['tax_report_id']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        comparison_context = self._build_comparison_context(data)
        data['form']['used_context'] = dict(comparison_context, lang=self.env.context.get('lang', 'en_US'))
        return self._print_report(data)


    def _print_report(self, data):
        data['form'].update(self.read([
            'date_from',
            'date_to',
            'tax_report_id',
            'target_move',
            'display_detail'
        ])[0])
        return self.env.ref('account_tax_report.action_report_tax_reg').report_action(self, data=data, config=False)
#         return self.env['report'].get_action(self, 'account_tax_report.report_tax_view', data=data)
