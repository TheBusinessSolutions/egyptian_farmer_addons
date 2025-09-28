# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Account Print Tax Report',
    'version' : '8.1.4',
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'license': 'Other proprietary',
    'price': 99.0,
    'currency': 'EUR',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/account_tax_report/276',#'https://youtu.be/X9LL44j8IUM',#'https://youtu.be/QuquMPVU5S8',
    'category' : 'Accounting/Accounting',
    'summary': 'Account Print Tax Report - Odoo',
    'description' : """
          This module adds the account tax report for odoo 9.
This module allows user to print tax report in Odoo version 9.0. Structure of tax report is build same like financial report.
User can configure taxes (Chart of taxes) and it will create the tax report hierarchy, and hierarchy will be used in print tax report.
We have added option to display details (Journal Items) on wizard which will allow user to analyse report in details.. 

Print Tax 
Print Tax Report
Odoo 9 Tax 
Odoo 9 Tax report
Chart of Taxes
Tax report
Community edition tax report
On Tax report cofiguration we have provided options (Same like financial report.):
Veiw
Taxes
Tax Tags
Report Value
Odoo tax report
odoo 10 tax report
taxes report
taxing
child taxes
bill tax
invoice tax

Menus:
Accounting/Configuration/Tax Reports
Accounting/Configuration/Tax Reports/Tax Reports
Accounting/Configuration/Tax Reports/Tax Reports Hierarchy
Accounting/Reporting/PDF Reports/Tax Report

    """,
    'website': 'https://www.probuse.com',
    'depends' : ['account'],
    'images': ['static/description/atp.jpg'],
    'data': ['views/tax_report_view.xml',
             'wizard/tax_report_wizard_view.xml',
             'report/report_reg.xml',
             'report/reporttax_view.xml',
             'security/ir.model.access.csv'],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
