# -*- coding: utf-8 -*-

{
    'name': 'Create Date: Stock Transfer List',
    'version': '15.0.1',
    'summary': """New field in the list view of stock transfer to show the time when the picking was created.""",
    'description': """New field in the list view of stock transfer to show the time when the picking was created.""",
    'category': 'Inventory/Inventory',
    'author': 'bisolv',
    'website': "",
    'license': 'AGPL-3',

    'price': 0.0,
    'currency': 'USD',

    'depends': ['stock'],

    'data': [
        'views/stock_picking.xml',
    ],
    'demo': [

    ],
    'images': ['static/description/banner.png'],
    'qweb': [],

    'installable': True,
    'auto_install': False,
    'application': False,
}

