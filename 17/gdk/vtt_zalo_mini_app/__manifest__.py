# -*- coding: utf-8 -*-

{
    'name': 'Vtt Zalo Mini App clone',
    'description': '''
    Zalo mini app cllone
    ''',
    'author': 'gtt',
    'application': True,
    'depends': [
        'base',
        'sale',
        'sale_loyalty',
        'vtt_base_address_vn',
        'delivery',        
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ir_cron_data.xml',
        'views/res_ward_views.xml',
        'views/delivery_carrier_views.xml',
        'views/company.xml',
        'views/partner.xml',        
        'views/sale_order.xml',
        'views/loyalty.xml',
        'views/product_template.xml',
        'views/product_category.xml',
        'views/zalo_news.xml',
        'views/menu.xml',
        'views/res_config_settings_views.xml',
        'wizard/update_shipping_price_view.xml',
        'wizard/partner_add_zalo_tag_wizard.xml',   
        'wizard/cancel_online_order_view.xml',
        'wizard/quick_create_partner_view.xml',
        'views/zalo_message_template_views.xml',
        'views/zalo_message_parameter_views.xml',
        'views/zalo_message_campaign_views.xml',
        'views/zalo_message_log_views.xml',     
        'views/zalo_webhook_data_views.xml',     
    ],
    'assets': {
        'web.assets_backend': [            
            'vtt_zalo_mini_app/static/src/xml/*',
            'vtt_zalo_mini_app/static/src/js/*',
            'vtt_zalo_mini_app/static/src/js/discuss/search_products_panel.xml',
            'vtt_zalo_mini_app/static/src/js/discuss/discuss_sidebar_categories.js',
            'vtt_zalo_mini_app/static/src/js/discuss/search_products_panel.js',
            'vtt_zalo_mini_app/static/src/js/discuss/thread_actions.js',
        ],
    },    
}