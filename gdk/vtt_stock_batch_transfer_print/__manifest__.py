# -*- coding: utf-8 -*-

{
    'name': 'Sale Stock Batch Transfer Pickings Print by VietTotal',
    'description': '''
    Allow to print Pickings Operation in Batch Transfer
    ''',
    'author': 'Evils',
    'depends': [
        'stock_picking_batch',
    ],
    'data': [
        'views/picking_batch_views.xml',
    ],
    'application': False
}