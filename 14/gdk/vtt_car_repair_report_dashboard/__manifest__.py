# -*- coding: utf-8 -*-

{
    'name': 'Car Repair Order Dashboard by VietTotal',
    'description': '''
    Car Repair Order Report Dashboard
    ''',
    'author': 'VietTotal',
    'application': False,
    'depends': [
        'vtt_web_dashboard',
        'vtt_car_repair',
    ],
    'data': [
        'report/report_views.xml',
    ]
}