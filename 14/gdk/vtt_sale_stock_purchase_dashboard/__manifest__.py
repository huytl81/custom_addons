# -*- coding: utf-8 -*-

{
    'name': 'Sale - Inventory - Purchase business Dashboard by VietTotal',
    'description': '''
    Provide features to show instant about Business health. A manager can get 
    how company worked, and effective of each group on total margin
    ''',
    'author': 'Evils',
    'application': True,
    'depends': [
        'vtt_board',
        'vtt_sale_report_dashboard',
        'vtt_purchase_report_dashboard',
        'vtt_stock_account_report_dashboard',
        'vtt_invoice_report_dashboard',
    ],
    'data': [
        'views/custom_dashboard_views.xml',
    ]
}