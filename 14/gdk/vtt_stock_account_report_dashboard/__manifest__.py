# -*- coding: utf-8 -*-

{
    'name': 'Stock Account modify for Dashboard by VietTotal',
    'description': '''
    Modify Odoo Stock Account Report for Dashboard display 
    ''',
    'author': 'Evils',
    'application': False,
    'depends': [
        'vtt_web_dashboard',
        'stock_account',
    ],
    'data': [
        'views/stock_valuation_views.xml',
    ]
}