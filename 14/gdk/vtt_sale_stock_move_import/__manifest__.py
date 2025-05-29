# -*- coding: utf-8 -*-

{
    'name': 'Sale Stock Picking Move Import by VietTotal',
    'description': '''
    Allow to import product move to Stock Picking.
    Allow to link Stock Picking to a Sale Order.
    ''',
    'author': 'Evils',
    'depends': [
        'sale_stock',
        'vtt_uom_code',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_views.xml',
        'views/sale_views.xml',
        'wizard/stock_move_import_wz_views.xml',
    ],
    'application': True
}