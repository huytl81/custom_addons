# -*- coding: utf-8 -*-

{
    'name': 'Custom Rating HR by VietTotal',
    'description': '''
    HR rating features.
    ''',
    'author': 'Evils',
    'application': False,
    'depends': [
        'vtt_custom_rating',
        'hr',
    ],
    'data': [
        'views/custom_rating_views.xml',
        'wizard/custom_rating_wz_views.xml',
    ]
}