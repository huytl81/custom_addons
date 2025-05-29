# -*- coding: utf-8 -*-

{
    'name': 'MRO Expansion',
    'description': '''
    MRO module expansion by VietTotal
    ''',
    'author': 'Evils',
    'application': False,
    'depends': [
        'car_repair_maintenance_service',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/project_data.xml',
        'views/project_task_views.xml',
        'views/support_views.xml',
    ]
}