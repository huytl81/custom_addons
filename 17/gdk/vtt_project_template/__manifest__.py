# -*- coding: utf-8 -*-

{
    'name': 'Project Template',
    # 'category': 'Hidden',
    'version': '1.0',
    'description': """
    Project Template Management by Viettotal.
        """,
    'depends': [
        'web',
        'project',
    ],
    # 'auto_install': True,
    'data': [
        'security/ir.model.access.csv',
        'data/default_project_data.xml',
        'views/project_template_views.xml',
        'views/project_template_task_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    # 'license': 'OEEL-1',
}
