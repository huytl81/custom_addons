# -*- coding: utf-8 -*-

{
    'name': 'My Anh Group Configuration',
    # 'category': 'Hidden',
    'version': '1.0',
    'description': """
My Anh Group Configuration by Viettotal.
        """,
    'depends': [
        'web',
        'mail',
        'vtt_base_setup',
        'analytic',
        'account_accountant',
        'sale_management',
        'stock',
        'project_todo',
        'purchase',
        'project_account',
        'vtt_hierarchy_list',
    ],
    # 'auto_install': True,
    'data': [
        'security/ir.model.access.csv',
        'data/myanh_default_config_data.xml',
        'data/default_project_data.xml',
        'report/project_report_views.xml',
        'views/project_views.xml',
        'views/project_type_views.xml',
        'views/project_task_reason_type_views.xml',
        'views/project_task_views.xml',
        'wizard/project_task_duplicate_wz_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    # 'license': 'OEEL-1',
}
