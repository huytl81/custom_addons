# -*- coding: utf-8 -*-

{
    'name': "Spreadsheet dashboard for MRO",
    'description': '''
    Spreadsheet Dashboard for MRO by VietTotal
    ''',
    'category': 'Repairs',
    'application': False,
    'version': '1.0',
    'auto_install': ['vtt_mro'],
    'depends': [
        'spreadsheet_dashboard',
        'vtt_mro'
    ],
    'data': [
        "data/mro_dashboards.xml",
    ],
}