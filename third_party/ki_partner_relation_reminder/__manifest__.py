# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.
{
    'name': "Send Notification on Customer/Vendor Business Relationship Anniversary",
    'summary': """ Send Notification on Customer/Vendor Business Relationship Anniversary """,
    'description': """
Send Notification on Customer/Vendor Business Relationship Anniversary
Business Relation
Notification
Reminder
Customer
Wishes
""",
    "version": "1.0",
    "category": "Tools",
    'author': "Kiran Infosoft",
    "website": "http://www.kiraninfosoft.com",
    'license': 'Other proprietary',
    'price': 0.0,
    'currency': 'EUR',
    'images': ['static/description/logo.png'],
    "depends": [
        'contacts'
    ],
    "data": [
        'views/partner_view.xml',
        'data/email_template.xml',
        'data/cron.xml'
    ],
    "application": False,
    'installable': True,
}
