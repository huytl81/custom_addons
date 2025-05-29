# -*- coding: utf-8 -*-

{
    'name': 'Unlock Sale Date Order by VietTotal',
    'description': '''
    Unlock Sale Date Order in "Sale" State
    ''',
    'author': 'Evils',
    'application': False,
    'depends': [
        'sale'
    ],
    'data': [
        'views/sale_order_views.xml',
    ]
}