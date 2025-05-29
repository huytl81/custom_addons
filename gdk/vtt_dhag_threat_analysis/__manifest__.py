# -*- coding: utf-8 -*-

{
    'name': 'DHAG Threat Analysis',
    'description': '''
    This module provide summary of solved-threat, and features to analysis information
    ''',
    'application': True,
    'depends': [
        'base',
        'mail',
        'vtt_widget_field_json_2columns',
    ],
    'data': [
        'views/templates.xml',
        'data/mapper_datas.xml',
        'data/suggest_datas.xml',
        'security/threat_security.xml',
        'security/ir.model.access.csv',
        'data/activity_datas.xml',
        'data/config_parameter_datas.xml',
        'data/threat.malware.activity.csv',
        'views/campaign_views.xml',
        'views/malware_views.xml',
        'views/investigate_malware_views.xml',
        'views/malware_activity_views.xml',
        'views/malware_property_views.xml',
        'views/malware_subject_views.xml',
        'views/investigate_views.xml',
        'views/location_views.xml',
        'views/subject_field_mapper_views.xml',
        'wizards/lastline_report_import_wz_views.xml',
        'wizards/campaign_import_wz_views.xml',
        'wizards/malware_hash_check_redir_wz_views.xml',
        'views/comparison_views.xml',
        'views/comparison_template_views.xml',
    ],
    'qweb': [
        'static/src/xml/button_templates.xml',
        'static/src/xml/field_file_paths.xml',
        'static/src/xml/malware_activity.xml',
    ],
}