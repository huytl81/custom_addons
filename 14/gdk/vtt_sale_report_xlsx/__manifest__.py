# -*- coding: utf-8 -*-

{
    'name': 'Sale Report XLSX by VietTotal',
    'description': '''
    Adding XLSX report action to Sale Quotation/ Order
    ''',
    'author': 'Evils',
    'application': False,
    'depends': [
        'sale',
        'vtt_report_xlsx',
    ],
    'data': [
        'data/default_datas.xml',
        'report/sale_reports.xml',
    ]
}