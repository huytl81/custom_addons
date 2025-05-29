# -*- coding: utf-8 -*-


{
    'name': 'Car Repair Fixed Discount by VietTotal',
    'sequence': 20,
    'category': 'Repairs',
    'summary': 'Allows to apply fixed amount of discount on Car Repair Request line',
    'description': """
Allows to apply fixed amount of discount on Car Repair Request line
""",
    'depends': ['vtt_car_repair', 'vtt_account_invoice_fixed_discount'],
    'data': [
        # 'security/repair_security.xml',
        # 'security/ir.model.access.csv',
        # 'data/sequence_data.xml',
        # 'report/order_report_templates.xml',
        # 'report/order_report.xml',
        # 'data/mail_data.xml',
        'views/order_views.xml',
        # 'views/service_type_views.xml',
        # 'views/vehicle_views.xml',
        # 'views/partner_views.xml',
        # 'views/stock_views.xml',
        # 'report/order_report_views.xml',
    ],
    'application': False,
}
