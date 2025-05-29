# -*- coding: utf-8 -*-

{
    'name': 'Vtt Zalo Mini App',
    'description': '''
    Zalo mini app
    ''',
    'author': 'gtt',
    'application': True,
    'depends': [
        'base', 'sale', 'sale_loyalty'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ir_cron_data.xml',
        'views/company.xml',
        'views/partner.xml',
        'views/sale_order.xml',
        'views/loyalty.xml',
        'views/product_template.xml',
        'views/product_category.xml',
        'views/zalo_news.xml',
        'views/menu.xml',
        'views/res_config_settings_views.xml'
    ],
}