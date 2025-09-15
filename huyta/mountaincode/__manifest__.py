# -*- coding: utf-8 -*-
{
    'name': "Lean & Lank Code",

    'summary': "Mèo béo ngáo ngơ",

    'description': """
        ... by Mèo béo ngáo ngơ
    """,

    'author': "Huy Ta",
    'website': "https://www.huyta.info",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Customize Application',
    'version': '6.9',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web'],
    'data': [
        'security/player_security.xml',
        'security/club_security.xml',
        'security/dog_security.xml',
        'security/cat_security.xml',
        'security/todo_task_security_groups.xml',
        'security/todo_task_manager_access.xml',
        'security/ir.model.access.csv',
        'views/club_view.xml',
        'views/player_view.xml',
        'views/dog_view.xml',
        'views/cat_view.xml',
        'wizards/dog_wizard_view.xml',
        'views/todo_task.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Services
            'mountaincode/static/src/services/todo_task_service.js',
            'mountaincode/static/src/services/user_service.js',

            # Form Component
            'mountaincode/static/src/xml/todo_task_popup_modal.xml',
            'mountaincode/static/src/js/todo_task_popup_modal.js',
            
            # Main Component - Must be last
            'mountaincode/static/src/xml/todo_task_action.xml',
            'mountaincode/static/src/js/todo_task_action.js',
        ]
    }

}
