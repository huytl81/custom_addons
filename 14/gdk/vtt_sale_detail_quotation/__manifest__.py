# -*- coding: utf-8 -*-

{
    'name': 'Sale Detail Quotation by VietTotal',
    'description': '''
    Allow to add products in note/ section line as detail in Quotation
    ''',
    'author': 'Evils',
    'application': False,
    'depends': [
        'sale',
        'web_domain_field',
    ],
    'data': [
        'views/assets.xml',
        'views/sale_order_views.xml',
    ]
}