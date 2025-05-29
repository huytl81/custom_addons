# -*- coding: utf-8 -*-

{
    'name': 'Vtt External API',
    'description': '''
    API for vtt External Access
    ''',
    'author': 'Evils',
    'application': True,
    'category': 'Ev API',
    'depends': [
        'base', 'sale', 'sale_loyalty'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/company.xml',
        'views/partner.xml',
        'views/sale_order.xml',
        'views/loyalty.xml',
        'views/product_template.xml',
        'views/product_category.xml',
        'views/zalo_news.xml',
        'views/menu.xml',
    ],
}