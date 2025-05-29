# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _, tools
from datetime import date, time, datetime
import logging

_logger = logging.getLogger(__name__)


class posOrder(models.Model):
	_inherit = 'pos.order'


	@api.model
	def create_from_ui(self, orders, draft=False):
		order_ids = super(posOrder, self).create_from_ui(orders, draft=False)
		loyalty_history_obj = self.env['all.loyalty.history']
		today_date = datetime.today().date() 
		config_loyalty_setting = self.env['all.loyalty.setting'].search([('active','=',True),('issue_date', '<=', today_date ),
							('expiry_date', '>=', today_date )])
		if config_loyalty_setting:
			for loyalty_setting in config_loyalty_setting:
				for order_id in order_ids:
					try:
						pos_order_id = self.browse(order_id.get('id'))
						if pos_order_id:
							if loyalty_setting.loyalty_tier.min_range <= pos_order_id.partner_id.total_sales <= loyalty_setting.loyalty_tier.max_range:
								ref_order = [o['data'] for o in orders if o['data'].get('name') == pos_order_id.pos_reference]
								for order in ref_order:
									cust_loyalty = pos_order_id.partner_id.loyalty_pts + order.get('loyalty')
									order_loyalty = order.get('loyalty')
									redeemed = order.get('redeemed_points')

									if order_loyalty > 0:
										vals = {
											'pos_order_id':pos_order_id.id,
											'partner_id': pos_order_id.partner_id.id,
											'loyalty_config_id' : loyalty_setting.id,
											'date' : datetime.now(),
											'transaction_type' : 'credit',
											'generated_from' : 'pos',
											'points': order_loyalty,
											'state': 'done',
										}
										loyalty_history = loyalty_history_obj.create(vals)	
							pos_order_id.partner_id.write({'tier_id': loyalty_setting.loyalty_tier.id})
					except Exception as e:
						_logger.error('Error in point of sale validation: %s', tools.ustr(e))
			
			return order_ids

			
class POSSession(models.Model):
	_inherit = 'pos.session'

	def _pos_ui_models_to_load(self):
		result = super()._pos_ui_models_to_load()
		result.extend(['loyalty.tier.config'])
		return result

	def _loader_params_loyalty_tier_config(self):
		today_date = datetime.today().date() 
		return {
			'search_params': {
				'fields': ['tier_name', 'min_range', 'max_range']
			}
		}

	def _get_pos_ui_loyalty_tier_config(self, params):
		return self.env['loyalty.tier.config'].search_read(**params['search_params'])


	def _loader_params_all_loyalty_setting(self):
		today_date = datetime.today().date() 
		return {
			'search_params': {
				'domain': [('active','=',True),('issue_date', '<=', today_date ),('expiry_date', '>=', today_date )], 
				'fields': ['name', 'product_id', 'issue_date', 'expiry_date', 'loyalty_basis_on', 'loyality_amount', 'active','redeem_ids','loyalty_tier']
			}
		}

	def _loader_params_res_partner(self):
		res = super(POSSession, self)._loader_params_res_partner()
		fields = res.get('search_params').get('fields')
		fields.extend(['total_sales','tier_id'])
		res['search_params']['fields'] = fields
		return res