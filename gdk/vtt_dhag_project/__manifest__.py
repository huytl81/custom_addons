# -*- coding: utf-8 -*-

{
    'name': 'DHAG Project',
    'description': '''
    Project modification for DHAG use-case
    ''',
    'application': False,
    'depends': [
        'project',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/checklist_views.xml',
        'views/task_views.xml',
    ],
}