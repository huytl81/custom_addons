{
    'name': 'Real Estate Ads - Sales Person',
    'version': '1.0',
    'category': 'Real Estate',
    'summary': 'Manage real estate properties and ads',
    'author': 'Huy Ta',
    'description': """
        Show real estate properties linked to sales person
    """,
    'depends': ['real_estate_ads','base', 'mail'],
    'data': [
        'views/res_users.xml',
    ],
    'demo': [
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
