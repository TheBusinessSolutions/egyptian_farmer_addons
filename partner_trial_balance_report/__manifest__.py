{
    'name': 'Partner Trial Balance Report',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Generate a trial balance report for partners',
    'description': """
    This module provides a trial balance report for partners.
    """,
    'author': 'Arun',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/partner_trial_balance_view.xml',
        'report/partner_trial_balance_template.xml',
        'report/partner_trial_balance_report.xml',
    ],
    'installable': True,
    'application': False,
}
