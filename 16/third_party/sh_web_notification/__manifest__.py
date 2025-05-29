# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name":   "Web Notification",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "license": "OPL-1",
    "category": "Website",
    "summary": "Web Push Notification,Website Push Notification, Website Notification,Website Custom Push Notification,Website Custom Notification,Web Notify,user Backend Notification, Web News Announcement,Web Client Notification,Notify User Odoo",   
    "description": """This module is useful to create a custom web notification. You can create and send instant web push notifications to users. You can send notifications in 3 ways, popup notification, animation & simple text notification.""",       
    "version": "16.0.2",
    "depends": [
        "base", "web","bus"
    ],
    "application": True,
    "data": [
        "security/sh_web_notification_groups.xml",
        "security/ir.model.access.csv",
        "views/annoucement_view.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'sh_web_notification/static/src/js/action_container.js',
            'sh_web_notification/static/src/scss/style.scss',
        ]
    },
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True,
    "price": 25,
    "currency": "EUR"
}
