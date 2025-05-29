# -*- coding: utf-8 -*-

{
    'name': 'Vietnamese Account Chart by VietTotal',
    'description': '''
    Vietnamese Account Chart by VietTotal
    ''',
    'application': False,
    'depends': [
        'l10n_vn',
        'account',
    ],
    'countries': ['vn'],
    'auto_install': ['l10n_vn'],
    'data': [],
    'post_init_hook': '_l10n_vn_vtt_post_init',
}