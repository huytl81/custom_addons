# -*- coding: utf-8 -*-

{
    'name': 'Inventory Report by VietTotal',
    'description': '''
    Inventory Period In/ Out Report by VietTotal
    ''',
    'author': 'Evils',
    'application': False,
    'depends': [
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_views.xml',
        'wizard/inventory_history_wz_views.xml',
        'wizard/stock_quantity_history_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ]
    }
}