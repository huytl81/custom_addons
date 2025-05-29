# -*- coding: utf-8 -*-

{
    'name': 'Sale Report Templates by VietTotal',
    'description': '''
    Provide VietTotal's featured sale templates
    ''',
    'author': 'Evils',
    'application': False,
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale_report_templates.xml',
        'data/paperformats.xml',
        'views/sale_views.xml',
    ]
}