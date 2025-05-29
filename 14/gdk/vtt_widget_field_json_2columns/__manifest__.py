# -*- coding: utf-8 -*-

{
    'name': 'VTT widgets',
    'description': 'Widgets module',
    'author': 'giaptt',
    'sequence': 2,
    'application': True,
    'depends': [
        'base',
        'web'
    ],
    'data': [
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/field_popup.xml',
        'static/src/xml/field_json_2_columns.xml',
    ]
}