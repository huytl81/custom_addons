# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

{

    'name': "Amount In Words",
    'version': '16.0.1',
    'summary': """Display Amount In Words in sale order, invoices and purchase orders, both in forms as well as reports| Amount |Words | amount in words| amount words| Total Amount | Total Amount in words|""",
    'description': """Display Amount In Words in sale order, invoices and purchase orders, both in forms as well as reports""",
    'license': 'OPL-1',
    'website': "https://www.kanakinfosystems.com",
    'author': 'Kanak Infosystems LLP.',
    'category': 'Sales/Sales',
    'depends': ['sale_management', 'purchase', 'account'],
    'data': [
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
        'views/invoice_view.xml',
        'report/sale_order_report.xml',
        'report/purchase_order_report.xml',
    ],
    'images': ['static/description/banner.gif'],
    'sequence': 1,
    "application": True,
    "installable": True,
}
