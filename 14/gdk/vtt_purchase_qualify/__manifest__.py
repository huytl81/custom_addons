# -*- coding: utf-8 -*-

{
    'name': 'Purchase Qualifying by VietTotal',
    'description': '''
    Provide Purchase Workflow User management
    ''',
    'author': 'Evils',
    'application': False,
    'depends': [
        'purchase',
    ],
    'data': [
        'views/purchase_views.xml',
        'views/config_settings_views.xml',
    ],
    'qweb': [],
    'sequence': 30
}