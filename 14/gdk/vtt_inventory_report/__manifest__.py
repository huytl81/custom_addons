# -*- coding: utf-8 -*-

{
    'name': 'Inventory Report Extend by VietTotal',
    'description': '''
    Provide Various Reports of Inventory
    ''',
    'author': 'Evils',
    'application': False,
    'depends': [
        'stock',
        'sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_template.xml',
        'wizards/inventory_history_view.xml',
        'views/stock_views.xml',
    ],
    'qweb': [
        'static/src/xml/inventory_report.xml',
    ],
    'sequence': 10
}