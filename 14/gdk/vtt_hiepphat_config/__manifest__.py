# -*- coding: utf-8 -*-

{
    'name': 'Custom Configure for HiepPhat by VietTotal',
    'description': '''
    Storing all customize for HiepPhat.
    ''',
    'author': 'Evils',
    'application': False,
    'depends': [
        'sale_stock',
        'sale_management',
        'purchase_stock',
        'vtt_sale_report_template',
        'web_domain_field',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/sale_reports.xml',
        'views/stock_views.xml',
        'views/sale_views.xml',
    ],
}