# -*- coding: utf-8 -*-

{
    'name': 'Custom Synchronize for Threat Data',
    'description': '''
    Synchronize feature between Base version - Local version
    ''',
    'author': 'Evils',
    'application': False,
    'depends': [
        'vtt_dhag_threat_analysis',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sync_config_views.xml',
        'views/sync_request_views.xml',
    ]
}