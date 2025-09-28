# -*- coding: utf-8 -*-

#from openerp import api, models, fields, _
#from openerp import SUPERUSER_ID
from odoo import api, models, fields, _
from odoo import SUPERUSER_ID

class TaxesReport(models.Model):
    _name = 'taxes.report'
    _description = 'Taxes Report'
    
#    @api.model_cr #This is to update level field of all financial reports which is compute field on report object.
    def init(self):
        report_ids = self.sudo().search([])
        for report in report_ids:
            self.sudo().write({'sequence': report.sequence})

#    @api.multi
    # @api.depends('parent_id', 'parent_id.level', 'children_ids', 'sequence', 'parent_id.sequence')
    @api.depends('parent_id', 'children_ids', 'sequence', 'parent_id.sequence')
    def _get_level(self):
        '''Returns a dictionary with key=the ID of a record and value = the level of this  
           record in the tree structure.'''
        for report in self:
            level = 0
            if report.parent_id:
                level = report.parent_id.level + 1
            report.level = level
    
    def _get_children_by_order(self):
        '''returns a recordset of all the children computed recursively, and sorted by sequence. Ready for the printing'''
        res = self
        children = self.search([('parent_id', 'in', self.ids)], order='sequence ASC')
        if children:
            res += children._get_children_by_order()

        result = {}
        for rec in res:
            result[rec.sequence] = rec
            
#         sorted_list = sorted(result.iteritems(), key=lambda key_value: key_value[0])
        sorted_list = sorted(result.items(), key=lambda key_value: key_value[0])
        
        final_res = self
        for s in sorted_list:
            final_res += s[1]

        return res
    
    name = fields.Char('Tax Name')
    sequence = fields.Integer('Sequence')
    parent_id = fields.Many2one('taxes.report', 'Parent')
    children_ids = fields.One2many('taxes.report', 'parent_id', 'Tax Report')
    level = fields.Integer(compute='_get_level', string='Level', store=True)
    type = fields.Selection([
        ('sum', 'View'),
        ('taxes', 'Taxes'),
#        ('tax_type', 'Tax Tags'),
#        ('tax_report', 'Report Value'),
        ], 'Type', default='sum')
    tax_ids = fields.Many2many('account.tax', 'account_tax_financial_report', 'report_line_id', 'tax_id', 'Taxes')
    tax_report_id = fields.Many2one('taxes.report', 'Report Value')
    tax_type_ids = fields.Many2many('account.account.tag', 'account_tax_report_type', 'report_id', 'tax_type_id', 'Tax Types', domain=[('applicability', '=', 'taxes')])
#    sign = fields.Selection([(-1, 'Reverse balance sign'), (1, 'Preserve balance sign')], 'Sign on Reports', required=True, default=1,
#                            help='For accounts that are typically more debited than credited and that you would like to print as negative amounts in your reports, you should reverse the sign of the balance; e.g.: Expense account. The same applies for accounts that are typically more credited than debited and that you would like to print as positive amounts in your reports; e.g.: Income account.')
    sign = fields.Selection(
            [('-1', 'Reverse balance sign'),
            ('1', 'Preserve balance sign')],
            'Sign on Reports',
            required=True,
            default='1',
            help='For accounts that are typically more debited than credited and that you would like to print as negative amounts in your reports, you should reverse the sign of the balance; e.g.: Expense account. The same applies for accounts that are typically more credited than debited and that you would like to print as positive amounts in your reports; e.g.: Income account.'
        )
    display_detail = fields.Selection([
        ('no_detail', 'No detail'),
        ('detail_flat', 'Display children flat'),
        ('detail_with_hierarchy', 'Display children with hierarchy')
        ], 'Display details', default='detail_flat')
    style_overwrite = fields.Selection([
#        (0, 'Automatic formatting'),
#        (1, 'Main Title 1 (bold, underlined)'),
#        (2, 'Title 2 (bold)'),
#        (3, 'Title 3 (bold, smaller)'),
#        (4, 'Normal Text'),
#        (5, 'Italic Text (smaller)'),
#        (6, 'Smallest Text'),
        ('0', 'Automatic formatting'),
        ('1', 'Main Title 1 (bold, underlined)'),
        ('2', 'Title 2 (bold)'),
        ('3', 'Title 3 (bold, smaller)'),
        ('4', 'Normal Text'),
        ('5', 'Italic Text (smaller)'),
        ('6', 'Smallest Text'),
        ], 'Tax Report Style', default=0,
        help="You can set up here the format you want this record to be displayed. If you leave the automatic formatting, it will be computed based on the financial reports hierarchy (auto-computed field 'level').")
    skip_display_base_amount = fields.Boolean('Skip Base Amount Display', help='Tick this box if you do not want to show base amount for this tax report. This can be used at top level tax report where amount comes wrong after summing up. It will show 0.0 always for that base amount.')


