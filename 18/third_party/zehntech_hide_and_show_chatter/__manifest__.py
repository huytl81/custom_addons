{
    "name": "Global Hide and Show Chatter",
    "description": """Global hide and show chatter is a feature in Odoo that allows users to 
    control access privileges to Chatter for all models""",
    'summary': "Global Hide and Show Chatter in Odoo is a feature that enables users to manage access to Chatter across all models, allowing control over its visibility based on user privileges.",
    "category": "Extra Tools",
    "sequence": 30,
    "version": "18.0.1.0.0",
    "author": "Zehntech Technologies Inc.",
    "company": "Zehntech Technologies Inc.",
    "maintainer": "Zehntech Technologies Inc.",
    "contributor": "Zehntech Technologies Inc.",
    "website": "https://www.zehntech.com/",
    "support": "odoo-support@zehntech.com",
    "depends": ['base', 'mail','crm','contacts'],
     "data": [
         'security/access_group.xml',
         'security/ir.model.access.csv',
         'views/res_group_view.xml',
         'views/res_users_view.xml',
     ],
    "assets": {
        "web.assets_backend": [
            "zehntech_hide_and_show_chatter/static/src/xml/chatter_topbar.xml",
            "zehntech_hide_and_show_chatter/static/src/xml/form_view.xml",
            "zehntech_hide_and_show_chatter/static/src/js/chatter_toggle.js",
            "zehntech_hide_and_show_chatter/static/src/css/button.css",

        ]
    },
   
    "images": [
        "static/description/banner.png"
    ],
    "license": "OPL-1",
    "installable": True,
    "application": False,
    "auto_install": False,
    "price": 00.00,
    "currency": "USD"
}
