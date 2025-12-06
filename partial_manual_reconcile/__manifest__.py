{
    "name": "Partial Reconcile",
    "version": "17.0.1.0",
    "category": "Accounting",
    "summary": "Partial Manual Reconcile",
    "author": "Opsway",
    "website": "https://opsway.com",
    "depends": [
        "account"
    ],
    "data": [
        "views/account_move_views.xml"
    ],
    "images": [
        "static/description/banner.png"
    ],
    "assets": {
        "web.assets_backend": [
            "/partial_manual_reconcile/static/src/js/reconciliation_model.js",
        ],
    },
    "application": True,
    "installable": True,
    "license": "LGPL-3",
}
