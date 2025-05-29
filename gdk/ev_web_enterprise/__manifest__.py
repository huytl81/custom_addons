# -*- coding: utf-8 -*-

{
    'name': 'Ev Web Enterprise',
    'category': 'Hidden',
    'version': '1.0',
    'description': """
Odoo Enterprise Web Client for self-explore.
        """,
    'depends': ['mail'],
    # 'auto_install': ['mail'],
    'data': [
        'data/viettotal_version_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # 'ev_web_enterprise/static/src/webclient/**/*.js',
            # 'ev_web_enterprise/static/src/webclient/settings_form_view/*.js',
        ],
    },
    'license': 'OEEL-1',
}
