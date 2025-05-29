# -*- coding: utf-8 -*-

{
    'name': 'Shipping GHN Integration',
    'version': '1.0',
    'description': """
    Shipping GHN Integration by VietTotal.
    """,
    'depends': [
        'sale_management',
        'sale_stock',
        'contacts',
        'delivery',
    ],
    # 'auto_install': True,
    'data': [
        'security/ir.model.access.csv',
        'data/res.country.state.csv',
        'views/res_partner.xml',
        'views/res_company.xml',
        'views/res_state_district_view.xml',
        'views/res_ward_view.xml',
        'views/stock_warehouse.xml',
        'views/sale_order_view.xml',
        'views/stock_picking.xml',
        'views/delivery_carrier_views.xml',
        'data/default_location_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    'license': 'LGPL-3',
}
