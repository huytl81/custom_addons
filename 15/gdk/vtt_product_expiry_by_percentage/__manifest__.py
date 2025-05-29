# -*- coding: utf-8 -*-

{
    'name': 'Products Expiration Percentage',
    'description': '''
    Products Expiration Date Alert by Percentage by VietTotal
    ''',
    'application': False,
    'author': 'Evils',
    'depends': [
        'product_expiry'
    ],
    'data': [
        'data/config_parameter_data.xml',
        'views/product_views.xml',
        'views/product_lot_views.xml',
        'views/stock_move_views.xml',
    ]
}