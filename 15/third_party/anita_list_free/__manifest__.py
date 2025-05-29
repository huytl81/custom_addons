# -*- coding: utf-8 -*-
{
    'name': "anita_list_free",

    'summary': """
        list view extend for odoo, powerfull listview for odoo, advance list manager for odoo!
        notice,this is the free version of anita_list,if you want to get the full version,please contact us!
    """,

    'description': """
    
        list view extend for odoo,
        list view manager,
        list view,
        list manager,
        
        table,
        tree table,
        expaned table,
        editable table,

        fixed table,
        fixed header table,
        fixed footer table,
        fixed header footer table,

        super table,
        advanced table,

        virtual list view,
        virtual list table,
        
        unlimit table,
        advance list manage for odoo,
        greate table
    """,

    'author': "funenc crax",
    'website': "https://odoo.funenc.com",
    'live_test_url': "http://odoo.funenc.com",
    'support': "odoo@funenc.com",

    'category': 'Apps/List',
    'version': '15.0.0.4',

    'price': 00,
    'currency': 'EUR',
    'license': 'OPL-1',

    'images': ['static/description/banner.png'],
    'depends': ['base', 'web'],

    'data': [
        'security/ir.model.access.csv',
        'views/anita_web.xml',
    ],

    'assets': {
        'web.assets_backend': [

            'anita_list_free/static/css/anita_list.scss',
            'anita_list_free/static/css/iconfont.css',
            'anita_list_free/static/libs/daterangepicker/daterangepicker.css',

            'anita_list_free/static/libs/resize_helper.js',
            'anita_list_free/static/libs/sortable.js',
            'anita_list_free/static/libs/daterangepicker/daterangepicker.js',

            # list view
            'anita_list_free/static/js/anita_list_controller.js',
            'anita_list_free/static/js/anita_list_render.js',
            'anita_list_free/static/js/anita_list_view.js',
            'anita_list_free/static/js/anita_list_model.js',
            'anita_list_free/static/js/anita_resize_manager.js',
            'anita_list_free/static/js/anita_util.js',
            'anita_list_free/static/js/anita_fake_view.js',

            # config
            'anita_list_free/static/js/config/anita_list_config.js',

            # search
            'anita_list_free/static/js/search/search_item_registry.js',
            'anita_list_free/static/js/search/anita_search_fields.js',
            'anita_list_free/static/js/search/anita_search_facet.js',
            'anita_list_free/static/js/search/anita_search_auto_complete.js',
            'anita_list_free/static/js/search/anita_auto_complete_sources.js',
            'anita_list_free/static/js/search/anita_search_auto_complete_source_registry.js',
            'anita_list_free/static/js/search/anita_search_row.js',

            # form
            'anita_list_free/static/js/form/anita_form_view.js',
            'anita_list_free/static/js/form/anita_form_render.js',
            'anita_list_free/static/js/form/anita_form_controller.js',
            'anita_list_free/static/js/form/anita_form_model.js',
        ],

        'web.assets_qweb': [
            'anita_list_free/static/xml/anita_list_view.xml',
            'anita_list_free/static/xml/anita_list_config.xml',
            'anita_list_free/static/xml/anita_search.xml',
            'anita_list_free/static/xml/anita_misc.xml',
        ]
    }
}
