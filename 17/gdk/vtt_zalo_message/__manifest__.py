# -*- coding: utf-8 -*-

{
    'name': 'VTT Zalo Message',
    'version': '1.0',
    'description': '''
        Vtt Zalo Message
    ''',
    'author': 'gtt',
    'application': False,
    'depends': [
        'vtt_zalo_mini_app',
    ],
    'data': [                
        'security/ir.model.access.csv',
        'views/ir_cron_data.xml',
        'views/zalo_message_template_views.xml',
        'views/zalo_message_parameter_views.xml',
        'views/zalo_message_campaign_views.xml',
        'views/zalo_message_log_views.xml',
        # 'wizard/zalo_message_campaign_wizard_views.xml',
    ],
}