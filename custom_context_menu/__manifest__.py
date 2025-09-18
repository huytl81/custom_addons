# -*- coding: utf-8 -*-
{
    "name": "Custom Context Menu | Odoo Custom Context Menu | Odoo Context Menu | Odoo Menus",
    'summary': 'Custom Context Menu for Odoo: Override and Enhance the Default Right-Click Experience',
    'description': '''
Transform the way you interact with Odoo!

This module completely overrides Odoo's default browser context menu, replacing it with a modern, customizable context menu designed for productivity and user experience. With this app, every right-click in Odoo becomes an opportunity to access relevant actions, shortcuts, and tools tailored to your business needs.

Key Features:
- Override Default Context Menu: Replaces the standard browser right-click menu with a fully integrated Odoo menu.
- Consistent User Experience: Ensures a unified, professional look and feel across your Odoo environment.
- Customizable Actions: Easily extend or modify the context menu to include the actions your users need most.
- Supports Nested Menus: Organize actions in parent/child structures for clarity and efficiency.
- Modern UI: Built with the latest Odoo frontend technologies for speed and responsiveness.
- Easy Installation: Plug-and-play—no technical expertise required.

Ideal for:
Odoo users and administrators who want to streamline workflows, provide quick access to common actions, and deliver a polished, professional interface.

Support & Documentation:
- Email: prt.c.bhatti@gmail.com

License: OPL-1
Compatible with: Odoo 18 Community & Enterprise
''',
    'author': "Preet Bhatti",
    'website': "https://preetbhatti.github.io/portfolio/",
    'category': 'Tools',
    'version': '18.0.0.0.0',
    'depends': ['web'],
    'assets': {
        'web.assets_backend': [
            ('include', 'web._assets_jquery'),
            'custom_context_menu/static/src/**/*',
        ],
    },
    'maintainer': 'Preet',
    'support': 'prt.c.bhatti@gmail.com',
    'images': ['static/description/banner.gif'],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}