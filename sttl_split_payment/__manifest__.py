# -*- coding: utf-8 -*-

{
    "name": 'Partial Amount Payment Matching',
    "version": "17.0.1.0",
    'description': """Partial Amount Payment Matching provides feature to create multiple split payment for invoices at once. """,
    "author": "Silver Touch Technologies Limited",
    'website': "https://www.silvertouch.com",
    'license': 'LGPL-3',
    'installable': True,
    'depends': ['account', 'mail', 'account_accountant', 'account_batch_payment'],
    'data': [
        'data/split_payment_sequence.xml',
        'wizard/remaining_payment_view.xml',
        "security/ir.model.access.csv",
        'views/account_payment.xml',
        'views/account_batch_payment.xml',
        'views/account_account_move.xml',
        'views/invoice_reconcile.xml',
    ],
    "images": ['static/description/banner.png'],
}
