# -*- coding: utf-8 -*-

{
    'name': 'Product Materials by VietTotal',
    'description': '''
    Allow to define Product Material that can use in other modules.
    ''',
    'author': 'Evils',
    'depends': [
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/product_material_views.xml',
        'views/product_views.xml',
    ],
    'qweb': [
        'static/src/xml/templates.xml'
    ],
    'application': False
}