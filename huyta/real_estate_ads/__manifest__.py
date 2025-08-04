{
    'name': 'Real Estate Ads',
    'version': '1.0',
    'category': 'Real Estate',
    'summary': 'Manage real estate properties and ads',
    'author': 'Huy Ta',
    'depends': ['base', 'mail'],
    'data': [
        'security/estate_groups.xml',
        'security/ir.model.access.csv',
        'views/property_view.xml',
        'views/property_type_view.xml',
        'views/property_tag_view.xml',
    ],
    'installable': True,
    'application': True,
}
