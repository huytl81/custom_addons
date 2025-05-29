# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Sale Delivery and Invoice Status in Odoo",
    "version": "16.0.1",
    "category" : "Sales",
    'license': 'OPL-1',
    'summary': 'This module helps the user to get the status of delivery and invoice of sale order also available filter for a sale order with full or partial delivery orders, fully or partially invoiced order.',
    "description": """
    
   This module helps the user to get the status of delivery and invoice of sale order also available filter for a sale order with full or partial delivery orders, fully or partially invoiced order. 
    
 Invoice Status
Sale Delivery Status
So status 
invoice status
status invoice
status of invoice
delivery status
bill status
biil status
status of bill
sale order status
status of Sale order
status of delivery order
delivery order status
delivery status 

    """,
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.in",
    "price": 000,
    "currency": 'EUR',
    "depends" : ['base','sale_management','stock','sale_stock'],
    "data": [
        'views/main_delivery_invoice.xml'
    ],
    'qweb': [
    ],
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/PKUFWyoUGcE',
    "images":["static/description/Banner.gif"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
