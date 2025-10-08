{
    'name': 'Customer Partner Ledger Report',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Generate a detailed customer ledger report',
    'author': 'SIMI Technologies',
    'website': 'https://simitechnologies.co.ke',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',

        # 'views/customer_ledger_menu.xml',
        'views/customer_ledger_wizard_view.xml',
        'views/customer_ledger_view.xml',
        
        'reports/customer_ledger_template.xml',
    ],
    'installable': True,
    'application': True,
}
