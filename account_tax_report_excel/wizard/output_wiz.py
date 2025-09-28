# -*- coding: utf-8 -*-
#from openerp import models, fields, api, _
from odoo import models, fields, api, _


class account_xls_output_tax_report(models.TransientModel):
    _name = 'account.xls.output.tax'
    _description = 'Wizard to store the Excel output'

    xls_output = fields.Binary(string='Excel Output', readonly=True)
    name = fields.Char(string='File Name', help="Save report as .xls format")
