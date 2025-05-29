# -*- coding: utf-8 -*-

{
    'name': 'Purchase Order Dashboard by VietTotal',
    'description': '''
    Purchase Order Report Dashboard
    ''',
    'author': 'Evils',
    'application': False,
    'depends': [
        'vtt_web_dashboard',
        'purchase',
    ],
    'data': [
        'report/report_views.xml',
    ]
}