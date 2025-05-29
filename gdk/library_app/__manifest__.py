# -*- coding: utf-8 -*-
{
    'name': "Library Management",

    'summary': """
        Manage library catalog and book lending.
    """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Huy Ta",
    "license": "LGPL-3",
    'website': "http://www.viettotal.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Library',
    'version': '16.5',

    # any module necessary for this one to work correctly
    "depends": ["base", "mail"],
    "application": True,
    # always loaded
    'data': [
        'data/data.xml',
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'views/library_book.xml',
        'views/library_book_category.xml',
        'views/book_list_template.xml',
        'views/res_partner_extend_view.xml',
        'views/library_book_rent.xml',
        'views/library_book_rent_wizard.xml',
        'views/library_book_return_wizard.xml',
        'views/res_config_settings_views.xml',
        'views/library_menu.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'data/res.partner.csv',
        'data/library.book.csv',
        'data/book_demo.xml'
    ],

    # 'post_init_hook': 'add_book_hook',
}
