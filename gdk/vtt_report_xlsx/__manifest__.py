# -*- coding: utf-8 -*-

{
    'name': 'XLSX External Generate Code by VietTotal',
    'description': '''
    Pretend Code string Model for customize XLSX report generate purpose
    ''',
    'application': False,
    'author': 'Evils',
    'depends': ['report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'views/xlsx_report_code_views.xml',
    ]
}