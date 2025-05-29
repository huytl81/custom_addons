# -*- coding: utf-8 -*-

{
    'name': 'Contact Owner Access rights by VietTotal',
    'description': '''
    With Own's Documents Right, user now just may access to own contact (except Users Ref)
    ''',
    'author': 'Evils',
    'application': False,
    'depends': [
        'base',
        'sales_team',
    ],
    'data': [
        'security/sale_security.xml',
        'security/ir.model.access.csv',
        'wizards/contact_user_wizard_views.xml',
    ]
}