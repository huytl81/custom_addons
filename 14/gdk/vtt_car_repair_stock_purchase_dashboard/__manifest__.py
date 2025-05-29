# -*- coding: utf-8 -*-

{
    'name': 'Car Repair - Inventory - Purchase Report by VietTotal',
    'description': '''
    Provide reports of Repair Order / Products Inventory / Purchase Order
    ''',
    'author': 'Evils',
    'application': True,
    'depends': [
        'vtt_board',
        'vtt_car_repair_report_dashboard',
        'vtt_purchase_report_dashboard',
        'vtt_stock_account_report_dashboard',
        'vtt_invoice_report_dashboard',
    ],
    'data': [
        'views/custom_dashboard_views.xml',
    ]
}