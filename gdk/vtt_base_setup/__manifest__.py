# -*- coding: utf-8 -*-

{
    'name': 'VietTotal Base Setup',
    # 'category': 'Hidden',
    'version': '1.0',
    'description': """
Base Setup module for VietTotal solutions.
        """,
    'depends': [
        'base',
        'web',
        'mail',
    ],
    'auto_install': False,
    'data': [
        'security/users_security.xml',
        'data/viettotal_version_data.xml',
        'data/users_data.xml',
        'data/default_config_data.xml',
        'views/webclient_templates.xml',
        'views/res_company_views.xml',
        'views/users_views.xml',
        'views/ir_attachment_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'vtt_base_setup/static/src/js/user_menu_items.js',
            'vtt_base_setup/static/src/js/web_title.js',
            # 'ev_web_enterprise/static/src/webclient/settings_form_view/*.js',
        ],
    },
    # 'license': 'LGPL-3',
}
