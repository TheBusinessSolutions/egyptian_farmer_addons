# -*- coding: utf-8 -*-

from odoo import models, fields, _

# to translate currency value in tafqeet
class ResCurrency(models.Model):
    _inherit = "res.currency"

    currency_unit_label = fields.Char(string="Currency Unit", help="Currency Unit Name",translate=True)
    currency_subunit_label = fields.Char(string="Currency Subunit", help="Currency Subunit Name",translate=True)

