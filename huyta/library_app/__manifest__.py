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
    'version': '3.0',

    # any module necessary for this one to work correctly
    "depends": ["base", "base_setup", "mail", "contacts", "website","utm"],
    "application": True,
    # "qweb": [
    #     'static/src/xml/qweb_template.xml',
    # ],
    # always loaded
    'data': [
        'data/data.xml',
        'data/library_stage.xml',
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/library_menu.xml',
        'views/library_book.xml',
        'views/library_book_category.xml',
        'views/book_list_template.xml',
        'views/res_partner_extend_view.xml',
        'views/library_book_rent.xml',
        'views/library_book_rent_wizard.xml',
        'views/library_book_return_wizard.xml',
        'views/templates.xml',
        'reports/book_rent_templates.xml',
        'reports/book_rent_report.xml',
        'reports/library_book_catalog_template.xml',
        'reports/library_book_report.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'data/res.partner.csv',
        'data/library.book.csv',
        'data/book_demo.xml'
    ],
    # 'post_init_hook': 'add_book_hook',
}
