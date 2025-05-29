# -*- coding: utf-8 -*-

{
    'name': 'Edu Admission Form by VietTotal',
    'description': '''
    Edu Admission website Form for guest register
    ''',
    'author': 'Evils',
    'application': False,
    'depends': [
        'openeducat_admission',
        'website_form',
        'vtt_multi_step_wizard',
    ],
    'data': [
        'security/edu_security.xml',
        'security/ir.model.access.csv',
        'data/model_datas.xml',
        'views/templates.xml',
        'views/website_menu_views.xml',
        'views/admission_views.xml',
        'views/student_views.xml',
        'views/fees_term_views.xml',
        'views/student_fees_views.xml',
        'report/student_course_report_templates.xml',
        'report/student_course_reports.xml',
        # 'wizard/mt_wz_views.xml',
        'views/assets.xml',
    ],
}