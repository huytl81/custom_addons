# -*- coding: utf-8 -*-

{
    'name': 'Custom Configure for DOVAXA by VietTotal',
    'description': '''
    Storing all customize for DOVAXA.
    ''',
    'author': 'Evils',
    'application': False,
    'depends': [
        'sale_stock',
        'sale_management',
        'vtt_sale_detail_quotation',
        'vtt_sale_report_xlsx',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/report_xlsx_datas.xml',
        'data/default_datas.xml',
        'report/sale_reports.xml',
        'views/assets.xml',
        'views/sale_views.xml',
    ],
}