# -*- coding: utf-8 -*-

{
    'name': 'Account Invoice Report modify for Dashboard by VietTotal',
    'description': '''
    Modify Odoo Account Invoice Report for Dashboard display 
    ''',
    'author': 'Evils',
    'application': False,
    'depends': [
        'vtt_web_dashboard',
        'account',
    ],
    'data': [
        'report/invoice_report_dashboard_views.xml',
        'views/account_move_views.xml',
    ]
}