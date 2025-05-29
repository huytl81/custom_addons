# -*- coding: utf-8 -*-

{
    'name': 'Vintech Configuration',
    # 'category': 'Hidden',
    'version': '1.0',
    'description': """
    Vintech Configuration by VietTotal.
        """,
    'depends': [
        'stock',
        'sale',
        'purchase',
        'account',
        'vtt_base_report_py3o',
        'report_pdf_py3o_preview',
        'vtt_stock_custom_import',
        'vtt_inventory_report',
    ],
    # 'auto_install': True,
    'data': [
        'views/stock_picking_views.xml',
        'views/stock_move_line_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    'license': 'LGPL-3',
}
