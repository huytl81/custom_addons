# -*- coding: utf-8 -*-

{
    'name': 'DHAG Threat Analysis Dashboard',
    'description': '''
    Threat Analysis Dashboard
    ''',
    'author': 'Evils',
    'application': False,
    'depends': [
        'vtt_dhag_threat_analysis',
        'vtt_board',
        'vtt_web_dashboard',
    ],
    'data': [
        'views/threat_custom_board_views.xml',
    ]
}