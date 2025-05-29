# -*- coding: utf-8 -*-

{
    'name': 'Partner Name Search Phone',
    # 'version': '1.0',
    'description': """
Partner Name Search Phone by Viettotal.
        """,
    'depends': [
        'base',
        'contacts',
    ],
    # 'auto_install': True,
    'data': [
        'views/res_partner_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    'license': 'LGPL-3',
}
