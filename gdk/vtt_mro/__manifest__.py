# -*- coding: utf-8 -*-

{
    'name': 'Maintenance, Repair & Operation by VietTotal',
    'description': '''
    Maintenance, Repair & Operation Management by VietTotal
    ''',
    'category': 'Repairs',
    'application': True,
    'version': '1.0',
    'auto_install': False,
    'depends': [
        'base',
        'web',
        'sale',
        'product',
        'stock',
        'contacts',
        'sale_stock',
        'account',
        # 'sale_management',
        'analytic',
    ],
    'data': [
        'security/mro_security.xml',
        'security/ir.model.access.csv',
        'data/config_data.xml',
        # 'data/analytic_data.xml',
        'data/sequence_data.xml',
        'data/plan_type_data.xml',
        'data/discuss_data.xml',
        'data/mail_templates.xml',
        'views/repair_order_views.xml',
        'views/equipment_views.xml',
        'views/repair_diagnosis_views.xml',
        'views/product_views.xml',
        'views/maintenance_plan_views.xml',
        'views/plan_type_views.xml',
        'views/repair_order_tag_views.xml',
        'views/res_partner_views.xml',
        'views/equipment_categ_views.xml',
        'views/warranty_ticket_views.xml',
        # 'views/repair_order_dashboard.xml',
        'report/repair_order_report_views.xml',
        'wizard/warranty_update_wz_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # '/vtt_mro/static/src/js/*.js',
            # '/vtt_mro/static/src/xml/*.xml',
        ]
    }
}