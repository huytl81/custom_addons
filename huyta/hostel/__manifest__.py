# -*- coding: utf-8 -*-
{
    'name': "Hostel Management",

    'summary': "Manage Hostel easily",

    'description': """
           Efficiently manage the entire residential 
           facility in the school.", # Supports reStructuredText(RST) 
           format (description is Deprecated)
    """,

    'author': "Huy Ta",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '18.0.0.1',
    'application': True,
    'installable':True,
    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'data/data.xml',
        'security/hostel_category_security.xml',
        'security/hostel_room_category_security.xml',
        'security/hostel_security.xml',
        'security/hostel_room_security.xml',
        'security/hostel_student_security.xml',
        'security/ir.model.access.csv',
        'views/hostel_category.xml',
        'views/hostel.xml',
        'views/hostel_room.xml',
        'views/hostel_student.xml',
        'views/hostel_room_category.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'web/static/src/xml/**/*',
        ],
    },
}

