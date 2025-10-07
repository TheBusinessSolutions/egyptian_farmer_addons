# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by CandidRoot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import fields,models,api,_
import calendar,io,base64
from odoo.tools.misc import xlsxwriter


class InventoryExcelReport(models.TransientModel):
    _name = "inventory.excel.report"
    _description = "Inventory Excel Report"

    categ_id = fields.Many2many('product.category', string="Product Category")

    xls_file = fields.Binary(string="XLS file")
    xls_filename = fields.Char()

    def excel_report(self):
        print("click**********")
        stock_quant = False
        if self.categ_id:
            print("if")
            stock_quant = self.env['stock.quant'].sudo().search([
                ('categ_id','in',self.categ_id.ids)
            ])
            print(" if stock_quant ::",len(stock_quant))
         
        else:
            print("else")
            stock_quant = self.env['stock.quant'].sudo().search([])
            print("else stock_quant ::",len(stock_quant))
            


        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Inventory Excel Report')

        main_dict = {}

        for quant in stock_quant:
            if quant.location_id.usage == 'internal':
                if quant.categ_id.id in main_dict:
                    main_dict[quant.categ_id.id]['qty'] += quant.quantity
                    main_dict[quant.categ_id.id]['line'] += [{
                            'product_name': quant.product_id.display_name,
                            'location_name': quant.location_id.display_name,
                            'lot_name': quant.lot_id.display_name,
                            'inventory_quantity': quant.quantity
                        }]
                else:
                    main_dict[quant.categ_id.id] = {
                        quant.categ_id.id : quant.categ_id.display_name,
                        'qty': quant.quantity,
                        'line': [{
                            'product_name':quant.product_id.display_name,
                            'location_name':quant.location_id.display_name,
                            'lot_name':quant.lot_id.display_name,
                            'inventory_quantity':quant.quantity
                        }]
                    }
        header_style = workbook.add_format({'bold': True, 'bg_color': '#dedede', 'align': 'center'})

        sheet.set_column('A0:D3', 25)

        sheet.write(0, 0, 'Product', header_style)
        sheet.write(0, 1, 'Location',  header_style)
        sheet.write(0, 2, 'Lot/Serial Number', header_style)
        sheet.write(0, 3, 'On Hand Quantity', header_style)

        categ_style = workbook.add_format({'bg_color': '#dedede'})

        row = 2
        for main in main_dict:
            sheet.write(row, 0, main_dict[main][main], categ_style)
            sheet.write(row, 1, '', categ_style)
            sheet.write(row, 2, '', categ_style)
            sheet.write(row, 3, main_dict[main]['qty'], categ_style)
            for line in main_dict[main]['line']:
                row += 1
                sheet.write(row, 0, line.get('product_name'))
                sheet.write(row, 1, line.get('location_name'))
                if line.get('lot_name'):
                    sheet.write(row, 2, line.get('lot_name'))
                else:
                    sheet.write(row, 2, '')

                sheet.write(row, 3, line.get('inventory_quantity'))
            row += 2

        workbook.close()
        xlsx_data = output.getvalue()
        self.xls_file = base64.encodebytes(xlsx_data)
        self.xls_filename = "Inventory Excel Report.xlsx"
        print("--xls_filename",self.xls_filename)
        return {
            'type': 'ir.actions.act_url',
            'name': 'Inventory Excel Report',
            'url': '/web/content/inventory.excel.report/%s/xls_file/%s?download=true' % (
                self.id, 'Inventory Excel Report.xlsx'),
        }