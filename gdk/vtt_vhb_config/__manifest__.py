# -*- coding: utf-8 -*-

{
    'name': 'Odoo configuration for VHB',
    # 'category': 'Hidden',
    # 'version': '1.0',
    'description': """
Odoo configuration for VHB by Viettotal.
        """,
    'depends': [
        'sale',
        'account',
        'vtt_base_report_py3o',
        'sale_project',
        'hr',
        'edit_order_date',
        'base_product_merge',
        'mrp',
        'purchase',
    ],
    'data': [
        'security/vhb_security.xml',
        'security/ir.model.access.csv',
        'views/account_payment_views.xml',
        'views/sale_order_views.xml',
        'views/stock_move_views.xml',
        'views/mrp_production_views.xml',
        'views/project_views.xml',
        'views/stock_quant_views.xml',
        'views/purchase_order_views.xml',
        'views/partner_views.xml',
        'views/users_views.xml',
        'wizard/project_create_wz_views.xml',
        'wizard/custom_sales_report_wz_views.xml',
        # 'report/vhb_custom_sales_report_views.xml',
        'report/mrp_production_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    'license': 'LGPL-3',
}
