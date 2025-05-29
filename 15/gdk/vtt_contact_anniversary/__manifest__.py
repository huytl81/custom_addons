# -*- coding: utf-8 -*-

{
    'name': 'Contact Anniversary Management by VietTotal',
    'description': '''
    This Module provide Advance Contact Management.
    The features included:
    - Contact Birthday
    - Contact Anniversary date 
    ''',
    'summary': 'Contact Anniversary date Advanced management by VietTotal',
    'category': 'Sales/CRM',
    'sequence': 10,
    'depends': [
        'contacts',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/config_parameter_data.xml',
        'data/cron_data.xml',
        'data/default_datas.xml',
        'views/anniversary_views.xml',
        'views/anniversary_category_views.xml',
        'views/partner_views.xml',
        # 'views/company_views.xml',
        'views/res_config_settings_view.xml',
    ],
    'author': 'Evils',
    'application': True
}