{
    'name': 'Real Estate Ads',
    'version': '1.0',
    'category': 'Real Estate',
    'summary': 'Manage real estate properties and ads',
    'author': 'Huy Ta',
    'depends': ['base', 'mail','website', 'web'],
    'data': [
        # Security
        # Access rules
        'security/access_groups.xml',
        'security/ir.model.access.csv',
        'security/property_type_access.xml',
        'security/property_tag_access.xml',
        # Record rules
        'security/record_rules.xml',
        # Views
        'views/property_view.xml',
        'views/property_offer_view.xml',
        'views/property_type_view.xml',
        'views/property_tag_view.xml',
        'views/property_web_template.xml',
        # Action
        'views/property_actions.xml',
        # Data files
        'data/property_type.xml',
        'data/estate.property.tag.csv',
        'data/mail_template.xml',
        # Report
        'report/report_template.xml',
        'report/property_report.xml',
    ],
    # Assets
    'assets': {
        'web.assets_backend': [
            'real_estate_ads/static/src/js/my_custom_tag.js',
            'real_estate_ads/static/src/xml/my_custom_tag_template.xml',
        ],
    },
    # Demo
    'demo': [
        'demo/property.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
