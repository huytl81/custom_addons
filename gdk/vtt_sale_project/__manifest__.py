# -*- coding: utf-8 -*-

{
    'name': 'Sale Project',
    # 'category': 'Hidden',
    'version': '1.0',
    'description': """
    Sale Project by Viettotal.
        """,
    'depends': [
        'web',
        'project',
        'sale',
        'sale_project',
    ],
    # 'auto_install': True,
    'data': [
        'security/ir.model.access.csv',
        'wizard/project_create_wz_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    'license': 'LGPL-3',
}
