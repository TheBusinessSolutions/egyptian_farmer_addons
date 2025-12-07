{
    'name': 'Product Creation Access for Stock Users',
    'version': '17.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Allow stock users to create and manage products',
    'description': """
        This module grants stock users the necessary permissions to:
        - Read, Write, and Create Products (product.template)
        - Read, Write, and Create Product Variants (product.product)
    """,
    'author': 'Business Solutions',
    'website': 'https://www.thebusinesssolutions.net',
    'depends': ['product', 'stock'],
    'data': [
        'security/product_security.xml',
        'security/ir.model.access.csv',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}