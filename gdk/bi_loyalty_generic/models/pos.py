# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _, tools
from datetime import date, time, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class pos_category(models.Model):
	_inherit = 'pos.category'
		
	Minimum_amount  = fields.Integer("Amount For loyalty Points")
	amount_footer = fields.Integer('Amount', related='Minimum_amount')

class pos_order(models.Model):
	_inherit = 'pos.order'

	@api.model
	def create_from_ui(self, orders, draft=False):
		order_ids = super(pos_order, self).create_from_ui(orders, draft=False)
		loyalty_history_obj = self.env['all.loyalty.history']
		today_date = datetime.today().date() 
		loyalty_setting = self.env['all.loyalty.setting'].search([('active','=',True),('issue_date', '<=', today_date ),
							('expiry_date', '>=', today_date )])
		if loyalty_setting:
			for order_id in order_ids:
				try:
					pos_order_id = self.browse(order_id.get('id'))
					if pos_order_id:
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
														
							if order.get('redeem_done') == True:
								vals = {
									'pos_order_id':pos_order_id.id,
									'partner_id': pos_order_id.partner_id.id,
									'loyalty_config_id' : loyalty_setting.id,
									'date' : datetime.now(),
									'transaction_type' : 'debit',
									'generated_from' : 'pos',
									'points': redeemed,
									'state': 'done',
								}
								loyalty_history = loyalty_history_obj.create(vals)
						
				except Exception as e:
					_logger.error('Error in point of sale validation: %s', tools.ustr(e))
			
		return order_ids

class POSSession(models.Model):
	_inherit = 'pos.session'


	def _loader_params_product_product(self):
		params = super()._loader_params_product_product()
		# this is usefull to evaluate reward domain in frontend
		params['search_params']['fields'].append('bi_pos_reports_catrgory')
		return params


	def _loader_params_pos_category(self):
		res = super(POSSession, self)._loader_params_pos_category()
		fields = res.get('search_params').get('fields')
		fields.extend(['Minimum_amount'])
		res['search_params']['fields'] = fields
		return res

	def _loader_params_res_partner(self):
		res = super(POSSession, self)._loader_params_res_partner()
		fields = res.get('search_params').get('fields')
		fields.extend(['loyalty_pts','loyalty_amount'])
		res['search_params']['fields'] = fields
		return res

	def _pos_ui_models_to_load(self):
		result = super()._pos_ui_models_to_load()
		result.extend(['all.loyalty.setting','all.redeem.rule'])
		return result

	def _loader_params_all_loyalty_setting(self):
		today_date = datetime.today().date() 
		return {
			'search_params': {
				'domain': [('active','=',True),('issue_date', '<=', today_date ),('expiry_date', '>=', today_date )], 
				'fields': ['name', 'product_id', 'issue_date', 'expiry_date', 'loyalty_basis_on', 'loyality_amount', 'active','redeem_ids']
			}
		}

	def _get_pos_ui_all_loyalty_setting(self, params):
		return self.env['all.loyalty.setting'].search_read(**params['search_params'])

	
	def _loader_params_all_redeem_rule(self):
		return {
			'search_params': {
				'domain': [], 
				'fields': ['reward_amt','min_amt','max_amt','loyality_id']
			}
		}

	def  _get_pos_ui_all_redeem_rule(self, params):
		return self.env['all.redeem.rule'].search_read(**params['search_params'])


	
		
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
