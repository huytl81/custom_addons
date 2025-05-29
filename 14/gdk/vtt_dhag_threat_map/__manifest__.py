# -*- coding: utf-8 -*-

{
    'name': 'DHAG Threat Map',
    'description': '''
    This module provide Map view of threat by location
    ''',
    'application': False,
    'depends': [
        'vtt_dhag_threat_analysis',
        'vtt_web_map',
    ],
    'data': [
        'views/location_views.xml',
    ],
}