# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _, tools
from datetime import datetime
from odoo import SUPERUSER_ID
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	total_sales = fields.Float(string='Total Sales', compute='update_total_sale')

	def update_total_sale(self):
		for record in self:
			partner_id = self.env['res.partner'].search([('id', '=', record.partner_id.id)])
			sale_id = self.search([('partner_id', '=', partner_id.id),('invoice_status', '=', 'invoiced')])
			pos_id = self.env['pos.order'].search([('partner_id', '=',  record.partner_id.id)])
			total_sale = 0
			if sale_id:
				for order in sale_id:
					for invoice in order.invoice_ids:
						if invoice.payment_state == 'paid':
							total_sale += order.amount_total
			if pos_id:
				total_sale += sum(order.amount_total for order in pos_id)
			record.total_sales = total_sale

	@api.constrains('total_sales')
	def update_loyalty_tier(self):
		for record in self:
			res_id = self.env['loyalty.tier.config'].search([('min_range', '<=', record.total_sales), ('max_range', '>=', record.total_sales)])
			if res_id:
				loyalty_config_id = self.env['all.loyalty.setting'].search(
					[('loyalty_tier.tier_name', '=', res_id.tier_name)])
				if loyalty_config_id.loyality_amount:
					record.order_credit_points = record.total_sales / loyalty_config_id.loyality_amount

	@api.model_create_multi
	def create(self, vals):
		result = super(SaleOrder, self).create(vals)
		if self.env.company.promotion_id:
			if self.env.company.from_date <= (result.create_date).date() <= self.env.company.to_date:
				if self.env.company.product_type == 'product':
					for line in result.order_line:
						if line.product_id in self.env.company.product_ids:
							line.order_id.write(
								{'order_credit_points': result.order_credit_points + self.env.company.promotion_points})
				if self.env.company.product_type == 'product_category':
					for line in result.order_line:
						if line.product_id.categ_id in self.env.company.product_category_ids:
							line.order_id.write(
								{'order_credit_points': result.order_credit_points + self.env.company.promotion_points})
		loyalty_history = self.env['all.loyalty.history'].search([('partner_id', '=', result.partner_id.id)])
		if self.env.company.sign_up_bonus:
			if not loyalty_history:
				vals = {
					'partner_id': result.partner_id.id,
					'points': self.env.user.company_id.sign_up_bonus,
					'state': 'done',
					'transaction_type': 'credit'
				}
				self.env['all.loyalty.history'].create(vals)
		return result


	def action_confirm(self):
		if not all(order._can_be_confirmed() for order in self):
			raise UserError(_(
				"The following orders are not in a state requiring confirmation: %s",
				", ".join(self.mapped('display_name')),
			))

		self.order_line._validate_analytic_distribution()

		for order in self:
			order.validate_taxes_on_sales_order()
			if order.partner_id in order.message_partner_ids:
				continue
			order.message_subscribe([order.partner_id.id])

		self.write(self._prepare_confirmation_values())

		# Context key 'default_name' is sometimes propagated up to here.
		# We don't need it and it creates issues in the creation of linked records.
		context = self._context.copy()
		context.pop('default_name', None)
		self.write(self._prepare_confirmation_values())

		# Context key 'default_name' is sometimes propagated up to here.
		# We don't need it and it creates issues in the creation of linked records.
		context = self._context.copy()
		context.pop('default_name', None)

		self.with_context(context)._action_confirm()
		if self.env.user.has_group('sale.group_auto_done_setting'):
			self.action_done()

		if self.env.su:
			self = self.with_user(SUPERUSER_ID)

		for order in self:
			if order.sale_order_template_id and order.sale_order_template_id.mail_template_id:
				order.sale_order_template_id.mail_template_id.send_mail(order.id)

		loyalty_history_obj = self.env['all.loyalty.history']
		today_date = datetime.today().date()
		config = self.env['all.loyalty.setting'].sudo().search([('active', '=', True), ('issue_date', '<=', today_date),
																('expiry_date', '>=', today_date)])
		for loop in config:
			if loop:
				for rec in self:
					if not rec.partner_id.loyalty_deactivate:
						if loop.loyalty_tier.min_range <= rec.total_sales <= loop.loyalty_tier.max_range:
							partner_id = rec.partner_id
							plus_points = 0.0
							company_currency = rec.company_id.currency_id
							web_currency = rec.pricelist_id.currency_id
							if loop.loyalty_basis_on == 'amount':
								if loop.loyality_amount > 0:
									price = sum(rec.order_line.filtered(lambda x: not x.is_delivery).mapped('price_total'))
									if company_currency.id != web_currency.id:
										if web_currency.rate != 0:
											new_rate = (price * company_currency.rate) / web_currency.rate
										else:
											new_rate = price
									else:
										new_rate = price
									plus_points = int(new_rate / loop.loyality_amount)

							if loop.loyalty_basis_on == 'loyalty_category':
								for line in rec.order_line:
									if not line.discount_line or not line.is_delivery:
										if rec.is_from_website:
											prod_categs = line.product_id.public_categ_ids
											for c in prod_categs:
												if c.Minimum_amount > 0:
													price = sum(rec.order_line.filtered(lambda x: not x.is_delivery).mapped('price_total'))
													if company_currency.id != web_currency.id:
														new_rate = (price * company_currency.rate) / web_currency.rate
													else:
														new_rate = price
													plus_points += int(new_rate / c.Minimum_amount)
										else:
											prod_categ = line.product_id.categ_id
											if prod_categ.Minimum_amount > 0:
												price = sum(rec.order_line.filtered(lambda x: not x.is_delivery).mapped('price_total'))
												if company_currency.id != web_currency.id:
													new_rate = (price * company_currency.rate) / web_currency.rate
												else:
													new_rate = price
												plus_points += int(new_rate / prod_categ.Minimum_amount)
							partner_id.write({'tier_id': loop.loyalty_tier.id})
							rec.write({'order_credit_points': rec.order_credit_points + plus_points})
						if rec.order_redeem_points > 0:
							is_debit = loyalty_history_obj.search(
								[('order_id', '=', rec.id), ('transaction_type', '=', 'debit')])
							if is_debit:
								is_debit.write({
									'points': rec.order_redeem_points,
									'state': 'done',
									'date': datetime.now(),
									'partner_id': rec.partner_id.id,
								})
							else:
								vals = {
									'order_id': rec.id,
									'partner_id': rec.partner_id.id,
									'date': datetime.now(),
									'transaction_type': 'debit',
									'generated_from': 'sale',
									'points': rec.order_redeem_points,
									'state': 'done',
								}
								loyalty_history_obj.sudo().create(vals)
		return True

	def action_cancel(self):
		res = super(SaleOrder, self).action_cancel()
		loyalty_history_obj = self.env['all.loyalty.history']
		for rec in self:
			loyalty = loyalty_history_obj.search([('order_id', '=', rec.id)])
			for l in loyalty:
				l.write({
					'state': 'cancel'
				})
		return res



class AccountMoveInherit(models.Model):
	_inherit = 'account.move'


	def generate_loyalty_points(self,move):
		if move.move_type == 'out_invoice':
			sale_order = self.env['sale.order'].search([('name','=',move.invoice_origin)],limit=1)	
			if sale_order:
				loyalty_history_obj = self.env['all.loyalty.history']   
				today_date = datetime.today().date()
				config = self.env['all.loyalty.setting'].sudo().search([('active','=',True),('issue_date', '<=', today_date ),
										('expiry_date', '>=', today_date )])
				for con in config:
					if con.loyalty_tier.min_range <= sale_order.partner_id.total_sales <= con.loyalty_tier.max_range:
						for rec in sale_order:
							partner_id =rec.partner_id
							plus_points = 0.0

							company_currency = rec.company_id.currency_id
							web_currency = rec.pricelist_id.currency_id     
							
							if con.loyalty_basis_on == 'amount' :
								if con.loyality_amount > 0 :
									price = sum(rec.order_line.filtered(lambda x: not x.is_delivery).mapped('price_total'))
									if company_currency.id != web_currency.id:
										new_rate = (price*company_currency.rate)/web_currency.rate
									else:
										new_rate = price
									plus_points =  int( new_rate / con.loyality_amount)

							if con.loyalty_basis_on == 'loyalty_category' :
								for line in  rec.order_line:
									if not line.discount_line or not line.is_delivery :
										if rec.is_from_website :
											prod_categs = line.product_id.public_categ_ids
											for c in prod_categs :
												if c.Minimum_amount > 0 :
													price = sum(rec.order_line.filtered(lambda x: not x.is_delivery).mapped('price_total'))
													if company_currency.id != web_currency.id:
														new_rate = (price*company_currency.rate)/web_currency.rate
													else:
														new_rate =price
													plus_points += int(new_rate / c.Minimum_amount)
										else:
											prod_categ = line.product_id.categ_id
											if prod_categ.Minimum_amount > 0 :
												price = sum(rec.order_line.filtered(lambda x: not x.is_delivery).mapped('price_total'))
												if company_currency.id != web_currency.id:
													new_rate = (price*company_currency.rate)/web_currency.rate
												else:
													new_rate = price
												plus_points += int(new_rate / prod_categ.Minimum_amount)
							
							if plus_points > 0 :
								is_credit = loyalty_history_obj.search([('order_id','=',rec.id),('transaction_type','=','credit')])
								if is_credit:
									is_credit.write({
										'points': (plus_points),
										'state': 'done',
										'date' : datetime.now(),
										'partner_id': partner_id.id,
									})

									move.write({'loyalty_genrate':True ,'genrated_points':(move.genrated_points + plus_points)})

								else:
									vals = {
										'order_id':rec.id,
										'partner_id': partner_id.id,
										'loyalty_config_id' : con.id,
										'date' : datetime.now(),
										'transaction_type' : 'credit',
										'generated_from' : 'sale',
										'points': plus_points,
										'state': 'done',
									}
									loyalty_history = loyalty_history_obj.sudo().create(vals)
									move.write({'loyalty_genrate':True ,'genrated_points':plus_points})
									self.write({'loyalty_genrate':True ,'genrated_points':plus_points})
								rec.write({'order_credit_points':plus_points})

		if move.move_type == 'out_refund':
			sale_order = self.env['sale.order'].search([('name','=',move.invoice_origin)],limit=1)
			if sale_order:
				loyalty_history_obj = self.env['all.loyalty.history']   
				today_date = datetime.today().date()
				config = self.env['all.loyalty.setting'].sudo().search([('active','=',True),('issue_date', '<=', today_date ),
										('expiry_date', '>=', today_date )])
				if con.loyalty_tier.min_range <= sale_order.partner_id.total_sales <= con.loyalty_tier.max_range:
					for rec in sale_order:
						if move.genrated_points <= rec.partner_id.loyalty_pts:
							partner_id =rec.partner_id
							plus_points = 0.0

							company_currency = rec.company_id.currency_id
							web_currency = rec.pricelist_id.currency_id     
							
							if config.loyalty_basis_on == 'amount' :
								if config.loyality_amount > 0 :
									price = sum(rec.order_line.filtered(lambda x: not x.is_delivery).mapped('price_total'))
									if company_currency.id != web_currency.id:
										new_rate = (price*company_currency.rate)/web_currency.rate
									else:
										new_rate = price
									plus_points =  int( new_rate / config.loyality_amount)

							if config.loyalty_basis_on == 'loyalty_category' :
								for line in  rec.order_line:
									if not line.discount_line or not line.is_delivery :
										if rec.is_from_website :
											prod_categs = line.product_id.public_categ_ids
											for c in prod_categs :
												if c.Minimum_amount > 0 :
													price = sum(rec.order_line.filtered(lambda x: not x.is_delivery).mapped('price_total'))
													if company_currency.id != web_currency.id:
														new_rate = (price*company_currency.rate)/web_currency.rate
													else:
														new_rate = price
													plus_points += int(new_rate / c.Minimum_amount)
										else:
											prod_categ = line.product_id.categ_id
											if prod_categ.Minimum_amount > 0 :
												price = sum(rec.order_line.filtered(lambda x: not x.is_delivery).mapped('price_total'))
												if company_currency.id != web_currency.id:
													new_rate = (price*company_currency.rate)/web_currency.rate
												else:
													new_rate = price
												plus_points += int(new_rate / prod_categ.Minimum_amount)
							
							if plus_points > 0 :
								is_credit = loyalty_history_obj.search([('order_id','=',rec.id),('transaction_type','=','credit')])
								if is_credit:
									is_credit.write({
										'points': - plus_points,
										'state': 'done',
										'date' : datetime.now(),
										'partner_id': partner_id.id,
									})
									move.write({'loyalty_genrate':False ,'genrated_points':move.genrated_points - plus_points})
								else:
									vals = {
										'order_id':rec.id,
										'partner_id': partner_id.id,
										'loyalty_config_id' : config.id,
										'date' : datetime.now(),
										'transaction_type' : 'credit',
										'generated_from' : 'sale',
										'points': -plus_points,
										'state': 'done',
									}
									loyalty_history = loyalty_history_obj.sudo().create(vals)
									move.write({'loyalty_genrate':True ,'genrated_points':plus_points})
									self.write({'loyalty_genrate':True ,'genrated_points':plus_points})
								rec.write({'order_credit_points':plus_points})