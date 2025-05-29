# -*- coding: utf-8 -*-

{
    'name': 'External Report Templates by VietTotal',
    'description': '''
    Provide Various Report Templates
    ''',
    'author': 'Evils',
    'application': False,
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'views/external_layouts.xml',
        'data/report_layout_data.xml',
    ],
    'qweb': [],
    'sequence': 10
}