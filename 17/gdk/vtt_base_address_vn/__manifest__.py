# -*- coding: utf-8 -*-

{
    'name': 'Vtt Base address VN',
    'version': '1.0',
    'description': """
    Vtt Base address VN
    """,
    'depends': [
        'contacts',
    ],
    # 'auto_install': True,
    'data': [
        'security/ir.model.access.csv',
        # 'data/res.country.state.csv',
        'views/res_partner.xml',
        'views/res_company.xml',
        'views/res_state_district_view.xml',
        'views/res_ward_view.xml',

        'data/default_location_data.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #     ],
    # },
    'license': 'LGPL-3',
}
