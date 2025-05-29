# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

{
    "name": "Cancel Inventory | Delete Stock Picking | Delete Inventory Adjustment | Delete Scrap Order | Delete Stock Moves",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Warehouse",
    "license": "OPL-1",
    "summary": "Stock Cancel, Cancel Inventory, Cancel Stock Picking, Cancel Inventory Adjustment, Cancel Scrap, Cancel Inventory Picking, Cancel Stock Adjustment, Cancel stock moves, Adjustment Cancel,delete inventory,remove inventory Odoo",
    "description": """This module helps to cancel stock-picking, stock adjustment, scrap orders & stock moves. You can also cancel multiple stock-picking, stock adjustment, scrap orders & stock moves from the tree view. You can cancel the stock-picking, stock adjustment & scrap orders in 3 ways,

1) Cancel Only: When you cancel the stock-picking, stock adjustment & scrap orders then the stock-picking, stock adjustment & scrap orders are cancelled and the state is changed to "cancelled".
2) Cancel and Reset to Draft: When you cancel the stock-picking, stock adjustment & scrap orders, first stock-picking, stock adjustment & scrap orders are cancelled and then reset to the draft state.
3) Cancel and Delete: When you cancel the stock-picking, stock adjustment & scrap orders then first the stock-picking, stock adjustment & scrap orders are cancelled and then the stock-picking, stock adjustment & scrap orders will be deleted.""",
    "version": "14.0.2",
    "depends": [
                "stock",

    ],
    "application": True,
    "data": [
        'security/stock_security.xml',
        'data/data.xml',
        'views/res_config_settings.xml',
        'views/views.xml',
    ],
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True,
    "price": 20,
    "currency": "EUR"
}
