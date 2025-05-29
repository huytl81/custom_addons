# -*- coding:utf-8 -*-

{
    'name': "VTT Official Dispatch",
    'summary': "Quản lý công văn",
    'description': """
       Quản lý công văn
                    """,
    'version': "1.0",
    'author': "",
    'website': "",
    'depends': ['base', 'hr', 'contacts'],

    'data': [
        'security/vtt_document_groups.xml',
        'security/ir.model.access.csv',
        'security/vtt_dispatch_document_security.xml',
        'data/ir_sequence_data.xml',
        'data/activity.xml',
        'wizards/vtt_dispatch_request_reject_action_views.xml',
        'views/vtt_document_views.xml',
        'views/vtt_document_request_views.xml',
        'views/vtt_document_category_views.xml',
        'views/vtt_document_actions.xml',
        'views/vtt_official_dispatch_receive.xml',
        'views/vtt_document_menu_items.xml',
        'views/vtt_res_company_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}
