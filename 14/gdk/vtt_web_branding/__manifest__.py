# -*- coding: utf-8 -*-

{
    'name': 'Odoo Web debranding by VietTotal',
    'description': '''
    Provide debrand Odoo title features
    ''',
    'summary': 'Odoo Web debrand by VietTotal',
    'website': 'http://www.viettotal.com',
    'category': 'Branding',
    'author': 'Evils',
    'application': False,
    'depends': [
        'web',
        'auth_signup',
    ],
    'data': [
        'data/default_datas.xml',
        'views/asset.xml',
        'views/templates.xml',
        'views/res_config_settings_view.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ]
}