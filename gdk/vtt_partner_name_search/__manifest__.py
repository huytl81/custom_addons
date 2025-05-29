# -*- coding: utf-8 -*-

{
    'name': 'Partner name search configuration',
    'description': '''
    Partner name search configuration by VietTotal
    ''',
    'author': 'Evils',
    'application': False,
    'depends': ['base_setup'],
    'data': [
        'data/default_datas.xml',
        'views/res_config_settings_views.xml',
    ],
    'sequence': 25
}