# -*- coding: utf-8 -*-

from odoo import models, fields, api, _,tools
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)

	
class ReedemptionLoyalty(models.TransientModel):
	_name = 'loyalty.wizard.reedem'
	_description = "Loyalty Redeem Wizard "

	order_credit_points = fields.Integer(string='Order Credit Points',copy=False)
	order_redeem_points = fields.Integer(string='Order Redeemed Points',copy=False)
	redeem_point=fields.Integer("Redemption Loyalty Point",copy=False)
	customer=fields.Char(string="Customer Name:",readonly=True,copy=False)
	loyalty_point=fields.Float(string="Your Loyalty Points (in point(s)):",readonly=True,copy=False)
	loyalty_balance=fields.Float(string="Your Loyalty Balance:",readonly=True,copy=False)

	@api.model
	def default_get(self, fields):  
		rec = super(ReedemptionLoyalty, self).default_get(fields)  
		active_ids = self._context.get('active_ids')
		result=self.env['sale.order'].browse(active_ids)
		if result:	
			today_date = datetime.today().date() 
			amt_total = result.amount_total
			partner_id =result.partner_id
			loyalty_pts = 0.0
			plus_points = 0.0
			redeem_value=0.0
			total_loyalty = 0.0
			config = self.env['all.loyalty.setting'].sudo().search([('active','=',True),('issue_date', '<=', today_date ),
								('expiry_date', '>=', today_date )])		
			
			for rule in config.redeem_ids:
				if rule.min_amt <= partner_id.loyalty_pts and partner_id.loyalty_pts <= rule.max_amt :
					redeem_value = rule.reward_amt
			loyalty_balance = round(redeem_value * partner_id.loyalty_pts ,2)
			
			rec.update({'customer':partner_id.name,
				'loyalty_point':partner_id.loyalty_pts,
				'loyalty_balance':loyalty_balance,       
			})
						
		return rec
	
	def ok_redeem(self):
		active_ids = self._context.get('active_ids')
		redeem_value=0.0		
		today_date = datetime.today().date()		
		result=self.env['sale.order'].browse(active_ids)
		partner_id =result.partner_id

		if self.redeem_point <= 0 :
			raise ValidationError(_('Please enter valid loyalty points'))				

		config = self.env['all.loyalty.setting'].sudo().search([('multi_company_ids','in',result.company_id.id),('active','=',True),('issue_date', '<=', today_date ),
							('expiry_date', '>=', today_date )])		
		if self.redeem_point > partner_id.loyalty_pts or self.redeem_point < 0:
			raise ValidationError(_('You can not redeem more than loyalty points'))				
		today_date = datetime.today().date()	
		is_exist= None
		if config:	
			point_amt = 0
			for rule in config.redeem_ids:
				if rule.min_amt <= partner_id.loyalty_pts  and   partner_id.loyalty_pts <= rule.max_amt :
					redeem_value = rule.reward_amt
					point_amt+=int(self.redeem_point) * redeem_value
			loyalty_balance = round(redeem_value * partner_id.loyalty_pts ,2)			
			if point_amt > result.amount_total:
				raise ValidationError(_('You can not redeem more than total amount'))							
			for line in result.order_line:				
				if config.product_id.id == line.product_id.id:					
					is_exist=line
					break				
			if not is_exist:
				self.env['sale.order.line'].sudo().create({
						'product_id': config.product_id.id,
						'name': config.product_id.name,
						'price_unit': -point_amt,
						'order_id': result.id,
						'product_uom':config.product_id.uom_id.id,
						'discount_line':True,
						'redeem_points' : int(self.redeem_point)
					})		
				result.update({			
					'order_redeem_points':self.redeem_point,
					'redeem_value' : point_amt,
				})
			else:	
				raise ValidationError(_('You can not redeem more than one time'))			
		return


