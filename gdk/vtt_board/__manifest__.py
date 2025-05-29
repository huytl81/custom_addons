# -*- coding: utf-8 -*-

{
    'name': 'Custom Board by VietTotal',
    'description': '''
    Features to manage Odoo Board
    ''',
    'author': 'Evils',
    'application': True,
    'depends': [
        'board',
    ],
    'data': [
        'security/board_security.xml',
        'security/ir.model.access.csv',
        'views/board_views.xml',
        'wizard/user_copy_board_wz_views.xml',
    ]
}