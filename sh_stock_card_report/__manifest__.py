# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Stock Card Report",
    "author": "Softhealer Technologies",
    "website": "http://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Warehouse",
    "license": "OPL-1",
    "summary": "Print Stock Card Report In PDF Stock Card Report In EXCEl Stock Card Report In XLS Product Stock Report Stock Rotation Report Real Time Stock In Real Time Stock Out Stock Ledger Report Incoming Ledger Outgoing Ledger Inventory Valuation Odoo Stock Movement Analysis Report Product Movement Analysis Report Stock Movement Report Inventory Movement Analysis Report Inventory Movement Report",
    "description": "Analyzing warehouse stock movements date with location-wise is made easy with this app. Easy to print report with group by product and it's category wise.",
    "version": "0.0.1",
    "depends": [
        'base_setup',
        'web', 
        'stock',
        ],
    "application": True,
    "data": [
        'security/sh_stock_card_groups.xml',
        'security/ir.model.access.csv',
        'report/sh_stock_card_report_templates.xml',
        'report/sh_stock_card_reports.xml',
        'wizard/sh_stock_card_report_wizard_views.xml',
    ],

    "auto_install": False,
    "installable": True,
    "images": ["static/description/background.png", ],
    "price": 40,
    "currency": "EUR"
}
