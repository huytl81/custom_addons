# -*- coding: utf-8 -*-

{
    'name': 'Custom Configure for Newday by VietTotal',
    'description': '''
    Storing all customize for Newday.
    ''',
    'author': 'Evils',
    'depends': [
        'product',
        'vtt_sale_report_xlsx',
        'vtt_sale_detail_quotation',
    ],
    'data': [
        'data/default_datas.xml',
        'data/report_xlsx_datas.xml',
        # 'report/product_reports.xml',
        'views/product_views.xml',
        'views/sale_views.xml',
    ],
    'application': False
}