# -*- coding: utf-8 -*-

{
    'name': 'Hierarchy List',
    # 'category': 'Hidden',
    'version': '1.0',
    'description': """
    Hierarchy List Base by Viettotal.
        """,
    'depends': [
        'base',
        'web',
    ],
    # 'auto_install': True,
    'data': [
    ],
    'assets': {
        'web.assets_backend': [
            'vtt_hierarchy_list/static/src/js/*.js',
            'vtt_hierarchy_list/static/src/xml/*.xml',
            # 'vtt_hierarchy_list/static/src/scss/*.scss',
        ],
    },
    'license': 'LGPL-3',
}
