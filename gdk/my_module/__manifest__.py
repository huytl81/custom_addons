# -*- coding: utf-8 -*-
{
    'name': "My New Module",  # Module title
    'description': """Long description""",  # You can also rst format
    'author': "Huy Ta",
    'website': "https://www.viettotal.com",
    'category': 'Uncategorized',
    'version': '16.0.1',
    'depends': ['base', 'account', 'mail', 'project', 'web_cohort', 'web_map'],
    #'depends': ['base', 'account', 'mail', 'project'],
    'data': [
        'views/my_contacts.xml',
        'views/my_tasks.xml'
    ],
    'application': True,
}
