# -*- coding: utf-8 -*-

{
    'name': 'DHAG Threat Analysis',
    'description': '''
    This module provide summary of solved-threat, and features to analysis information
    ''',
    'application': True,
    'depends': [
        'base',
        'web',
        'mail',
        'calendar',
        'contacts',
        'project',
        'auditlog',
        'vtt_dhag_home_title',
        # 'web_responsive',
    ],
    'post_init_hook': 'create_default_audit_rule',
    'data': [
        'security/threat_security.xml',
        'security/ir.model.access.csv',
        'data/activity_datas.xml',
        'data/mapper_datas.xml',
        'data/suggest_datas.xml',
        'data/config_parameter_datas.xml',
        'data/threat.malware.activity.csv',
        'data/compare_template_datas.xml',
        'data/default_config.xml',
        'views/campaign_views.xml',
        'views/location_views.xml',
        'views/malware_views.xml',
        'views/investigate_views.xml',
        # 'views/investigate_malware_views.xml',
        'views/malware_activity_views.xml',
        'views/malware_property_views.xml',
        'views/malware_subject_views.xml',
        'views/subject_field_mapper_views.xml',
        'views/comparison_views.xml',
        'views/comparison_template_views.xml',
        'views/calendar_views.xml',
        'wizard/campaign_import_wz_views.xml',
        'wizard/lastline_report_import_wz_views.xml',
        'wizard/malware_hash_check_redir_wz_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    'license': 'LGPL-3',
}