# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by CandidRoot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import fields,models,api,_


class StockQuant(models.Model):
    _inherit = "stock.quant"

    categ_id = fields.Many2one(related="product_id.categ_id", string="Product Category", store=True)


