# -*- coding: utf-8 -*-

{
    'name': 'Execute Python Code extension by Evils',
    'description': '''
    Add sequence, notice, colors to execute-python-code model.
    ''',
    'author': 'Evils',
    'application': True,
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/python_code_views.xml'
    ],
}