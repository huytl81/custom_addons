# -*- coding: utf-8 -*-

{
    'name': 'Request for Supply',
    'category': 'Inventory',
    'version': '1.0',
    'description': """
    Request for Supply by VietTotal.
    """,
    'depends': [
        'mail',
        'stock',
        'purchase',
        'purchase_stock',
    ],
    # 'auto_install': True,
    'data': [
        'security/supply_request_security.xml',
        'security/ir.model.access.csv',
        'data/config_setting_default.xml',
        'data/sequence_data.xml',
        'views/supply_request_views.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #     ],
    # },
    'license': 'LGPL-3',
}
