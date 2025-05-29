 # -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
	'name': 'Multi Warehouse Product Low Stock Notification Alert',
	'version': '15.0.1',
	'category': 'Warehouse',
	'summary': 'Product low stock alerts for multi warehouse product stock alerts on product low stock notification on product stock alerts multi warehouse product stock alerts product Low Stock Report Minimum Stock Reminder Email Stock notify Email product stock alert',
	'description': """ This odoo app helps user to get email notification for low stock product based on on hand or forcasted quantity. User can also set notification mode based on global, individual, or reorder rule based. User can set minimum quantity for product and product variant, Only configured user will get email notification for low stock product. """,
	'author':'BrowseInfo',
	'website': 'https://www.browseinfo.in',
	"price": 20,
	"currency": 'EUR',
	'depends': ['base','sale_management','stock','bi_product_low_stock_notification'],
	'data': [
	'security/ir.model.access.csv',
	'view/email_templete.xml',
	'report/low_stock_report_template.xml',	
	],
	'license':'OPL-1',
	'test': [],
	'demo': [],
	'css': [],
	'installable': True,
	'auto_install': False,
	'application': False,
	'live_test_url':'https://youtu.be/JVX3co52EAg',
	"images":['static/description/Banner.png'],
}


