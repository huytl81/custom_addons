# -*- coding: utf-8 -*-

{
    'name': 'Sale Project Template',
    # 'category': 'Hidden',
    'version': '1.0',
    'description': """
    Project Creating while Confirmed a Sale Order by Viettotal.
        """,
    'depends': [
        'vtt_project_template',
        'sale_management',
    ],
    # 'auto_install': True,
    'data': [
        'views/sale_order_template_views.xml',
        'views/sale_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    # 'license': 'OEEL-1',
}
