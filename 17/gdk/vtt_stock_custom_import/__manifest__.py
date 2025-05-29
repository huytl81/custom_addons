# -*- coding: utf-8 -*-

{
    'name': 'Stock Custom Import',
    # 'category': 'Hidden',
    'version': '1.0',
    'description': """
    Stock Custom Import by Viettotal.
        """,
    'depends': [
        'stock',
    ],
    # 'auto_install': True,
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_type_views.xml',
        'views/stock_picking_views.xml',
        'wizard/stock_custom_import_wz_views.xml',
        'wizard/stock_picking_move_import_wz_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    'license': 'LGPL-3',
}
