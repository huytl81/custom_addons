# -*- coding: utf-8 -*-


{
    'name': 'Car Repair Management by VietTotal',
    'sequence': 3,
    'category': 'Repairs',
    'summary': 'Manager Car Repair Request',
    'description': """
Manage Car repair request by Ticket.
====================================================================

The following topics are covered by this module:
------------------------------------------------------
    * Create repair Ticket
    * Manage Car/ Vehicle
    * Invoicing
    * Warranty concept
    * Repair quotation report
    * Notes for the technician and for the final customer
""",
    'depends': ['stock', 'account', 'fleet', 'sale', 'web_domain_field'],
    'data': [
        'security/repair_security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'report/order_report_templates.xml',
        'report/order_report.xml',
        'data/mail_data.xml',
        'views/repair_order_views.xml',
        'views/service_type_views.xml',
        'views/vehicle_views.xml',
        'views/partner_views.xml',
        'views/stock_views.xml',
        'report/order_report_views.xml',
    ],
    'application': True,
    'qweb': [
        'static/src/xml/*.xml',
    ],
}
