# -*- coding: utf-8 -*-
{
    'name': "HSPL Maintenance Mode",

    'summary': """
        HSPL Maintenance Mode
        """,

    'description': """
        HSPL Maintenance Mode
    """,

    'author': "Heliconia Solutions Pvt. Ltd.",
    'website': "https://heliconia.io/",

    'category': 'web',
    'version': '14.0.0.1',

    'depends': ['base_setup', 'web', 'website'],

    'data': [
        'views/res_config_settings.xml',
        'views/assets.xml',
        'views/templates.xml',
    ],
    'images': ['static/description/icon.jpg'],

    'installable': True,
    'auto_install': False,
    'application': True,
}
