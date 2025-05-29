# -*- coding: utf-8 -*-

{
    'name':'Admin page Configuration',
    'description':'Admin page Configuration',
    'author':'Evils',
    'application':True,
    'depends':[
        'web',
        'base',
    ],
    'data':[
        'security/users_security.xml',
        'views/user_views.xml',
        'data/user_data.xml',
    ],
    'website': 'http://www.viettotal.vn',
    'category': 'Web',
    'summary': 'Admin page configuration for simple user maintain purpose',
    'qweb': [],
}