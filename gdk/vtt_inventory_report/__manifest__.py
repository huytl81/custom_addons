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
    ],
    'assets': {
        'web.assets_backend': [
            'vtt_inventory_report/static/src/js/inventory_report_list_controller.js',
            'vtt_inventory_report/static/src/js/inventory_report_list_view.js',
        ]
    }
}