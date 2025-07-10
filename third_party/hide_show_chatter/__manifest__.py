{
    "name": "Global Hide and Show Chatter",
    "description": """Global hide and show chatter is a feature in Odoo that allows users to 
    control access privileges to Chatter for all models""",
    'summary': "Global Hide and Show Chatter in Odoo is a feature that enables users to manage access to Chatter across all models, allowing control over its visibility based on user privileges.",
    "category": "Extra Tools",
    "sequence": 30,
    "version": "18.0.1.0.0",
    "author": "Huy Ta",
    "company": "Huy Ta",
    "maintainer": "Huy Ta",
    "contributor": "Huy Ta",
    "website": "https://www.httech.com/",
    "support": "talehuy81@gmail.com",
    "depends": ['base', 'mail','crm','contacts'],
     "data": [
         'security/access_group.xml',
         'security/ir.model.access.csv',
         'views/res_group_view.xml',
         'views/res_users_view.xml',
     ],
    "assets": {
        "web.assets_backend": [
            "hide_show_chatter/static/src/xml/chatter_topbar.xml",
            "hide_show_chatter/static/src/xml/form_view.xml",
            "hide_show_chatter/static/src/js/chatter_toggle.js",
            "hide_show_chatter/static/src/css/button.css",

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
