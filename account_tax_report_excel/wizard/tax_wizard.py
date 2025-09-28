# -*- coding: utf-8 -*-
import time
import xlwt
import io
# import cStringIO
import base64
#from openerp import api, models, fields, _
from odoo import api, models, fields, _
import sys
import os

class TaxReportWizard(models.TransientModel):
    _inherit = "tax.report.wizard"

    print_in_excel = fields.Boolean('Print In Excel?')

    @api.model
    def render_header(self, ws, fields, first_row=0):
        header_style = xlwt.easyxf('font: name Helvetica,bold on, height 260')
        col = 0
        for hdr in fields:
            ws.write(first_row, col, hdr, header_style)
            ws.row(first_row ).height_mismatch = True
            ws.row(first_row).height = 350
            col += 1
        return first_row + 2

#    @api.multi
    def _print_in_excel(self, data):
        workbook = xlwt.Workbook()
        data['form'].update(self.read(['date_from', 'date_to', 'tax_report_id', 'target_move', 'display_detail'])[0])
        tax_report = self.env['taxes.report'].search([('id', '=', data['form']['tax_report_id'][0])])
        sheet = workbook.add_sheet(tax_report.name)
        sheet.row(0).height = 256*3
        title_style = xlwt.easyxf('font: name Times New Roman,bold on, italic on, height 600')
        title_style2 = xlwt.easyxf('font: name Times New Roman,bold on, italic on, height 240')
        title_style1 = xlwt.easyxf('font: name Times New Roman,bold on, height 240')
        al = xlwt.Alignment()
        al.horz = xlwt.Alignment.HORZ_CENTER
        title_style.alignment = al
        if data['form']['display_detail']:
            sheet.write_merge(0, 0, 0, 5, tax_report.name, title_style)
            row = self.render_header(sheet, ['Name']+ [] + ['Tax Amount'] + [] + ['Base Amount'] + [] + ['Partner Name '] + [] + ['Journal Date'] + [] + ['Ref'], first_row=7)
            n = 'Tax Report'
            sheet.write_merge(2, 2, 0, 5, tax_report.name + '---'+ n, title_style2)
        else:
            sheet.write_merge(0, 0, 0, 2, tax_report.name, title_style)
            row = self.render_header(sheet, ['Name']+ [] + ['Tax Amount'] + [] + ['Base Amount'], first_row=7)
            n = 'Tax Report'
            sheet.write_merge(2, 2, 0, 2, tax_report.name + '---'+ n, title_style2)

        if data['form']['date_from'] and data['form']['date_to'] :
            sheet.write(3, 0, 'Date From', title_style1)
#            sheet.write(3, 1, data['form']['date_from'].strftime('%Y-%m-%d'), title_style1)
            sheet.write(3, 1, fields.Date.to_string(data['form']['date_from']), title_style1)
            sheet.write(4, 0, 'Date To', title_style1)
#            sheet.write(4, 1, data['form']['date_to'].strftime('%Y-%m-%d'), title_style1)
            sheet.write(4, 1, fields.Date.to_string(data['form']['date_to']), title_style1)
            sheet.row(2).height_mismatch = True
            sheet.row(2).height = 300
            sheet.row(3).height_mismatch = True
            sheet.row(3).height = 300
            sheet.row(4).height_mismatch = True
            sheet.row(4).height = 300

        tax_data = self.env['report.account_tax_report.report_tax_view'].get_tax_lines(data['form'])

        value_style = xlwt.easyxf('font: name Helvetica,bold on')

        value_style1 = {1: xlwt.easyxf('font: name Helvetica,bold on, height 260'),
                       2: xlwt.easyxf('font: name Helvetica,bold on, height 240'),
                       3: xlwt.easyxf('font: name Helvetica,bold on, height 200'),
                       4: xlwt.easyxf('font: name Helvetica,bold on, height 200'),
                       5: xlwt.easyxf('font: name Helvetica,bold on, height 200'),
                       6: xlwt.easyxf('font: name Helvetica, height 200'),
                       7: xlwt.easyxf('font: name Helvetica,bold on, height 200')}

        cell_count = 0
        col_width = 0

        for value in tax_data:
            value['level'] = int(value['level'])#odoo13
            if value['level'] == 0:
                continue

            margin_space = ''
            if not value['level'] == 1:
                margin_space = ' ' * value['level']
            sheet.write(row,cell_count, margin_space + value['name']
                        ,value_style1[value['level']+1])
            col = sheet.col(cell_count) 
            sheet.row(row).height_mismatch = True
            sheet.row(row).height = 350
            if len(value['name']) > col_width:
                col_width = len(value['name']) 
                col.width = 256 * (col_width + 5)
            cell_count += 1

            sheet.write(row,cell_count,value['tax_amount'] * int(value['sign'])#value['sign'] 
                        , value_style1[value['level']+1])
            col = sheet.col(cell_count) 
            col.width = 256 * 16
            cell_count += 1

            sheet.write(row,cell_count,value['base_amount'] * int(value['sign'])#value['sign']
                        ,value_style1[value['level']+1])
            col = sheet.col(cell_count) 
            col.width = 256 * 16
            cell_count += 1

            if value.get('partnername'):
                sheet.write(row,cell_count,value['partnername'] 
                        ,value_style1[value['level']+1])
                col = sheet.col(cell_count) 
                col.width = 256 * 16
                cell_count += 1
            if value.get('date'):
                sheet.write(row,cell_count,fields.Date.to_string(value['date']) 
                        ,value_style1[value['level']+1])
                col = sheet.col(cell_count) 
                col.width = 256 * 16
                cell_count += 1
            if value.get('ref'):
                sheet.write(row,cell_count,value['ref'] 
                        ,value_style1[value['level']+1])
                col = sheet.col(cell_count) 
                col.width = 256 * 16
                cell_count += 1

            row += 1
            cell_count = 0
#         stream = cStringIO.StringIO()
        stream = io.BytesIO() # odoo11
        workbook.save(stream)
#         self.env.cr.execute(""" DELETE FROM account_xls_output_tax """)

        attach_id = self.env['account.xls.output.tax'].create({
            'name':'Tax Report.xls',
            'xls_output': base64.encodebytes(stream.getvalue())
        })
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.xls.output.tax',
            'res_id':attach_id.id,
            'type': 'ir.actions.act_window',
            'target':'new'
        }

#    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['tax_report_id', 'date_from', 'date_to', 'target_move', 'print_in_excel'])[0]
        if not data['form']['print_in_excel']:
            return super(TaxReportWizard, self).check_report()
        else:
            for field in ['tax_report_id']:
                if isinstance(data['form'][field], tuple):
                    data['form'][field] = data['form'][field][0]
            comparison_context = self._build_comparison_context(data)
            data['form']['used_context'] = dict(comparison_context, lang=self.env.context.get('lang', 'en_US'))
            return self._print_in_excel(data)
