# -*- coding: utf-8 -*-

{
    'name': 'Custom Configure for Tiendatco by VietTotal',
    'description': '''
    Storing all customize for Tiendatco.
    ''',
    'author': 'Evils',
    'depends': [
        'vtt_product_material',
        'vtt_uom_code',
        'vtt_report_xlsx',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/default_datas.xml',
        'report/product_reports.xml',
        'views/product_material_views.xml',
    ],
    'application': False
}