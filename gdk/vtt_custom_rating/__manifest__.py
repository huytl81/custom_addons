# -*- coding: utf-8 -*-

{
    'name': 'Custom Model Rating by VietTotal',
    'description': '''
    Custom Model Rating features.
    This module is technical module.
    ''',
    'author': 'Evils',
    'application': False,
    'depends': [
        'base',
        'contacts',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/custom_rating_views.xml',
        'wizard/custom_rating_wz_views.xml',
    ]
}