# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _, tools
from datetime import date, time, datetime
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError


class resPartner(models.Model):
	_inherit = 'res.partner'

	loyalty_deactivate = fields.Boolean('Loyalty Deactive')
	tier_id = fields.Many2one('loyalty.tier.config', string='Loyalty Tier')
	total_sales = fields.Float(string='Total Sales', compute='update_total_sale')
	ribbon_color = fields.Integer('Ribbon Color', related='tier_id.ribbon_color', store=True)
	ribbon_text = fields.Char('Ribbon Text', related='tier_id.ribbon_text', store=True)
	red = fields.Boolean('Red', compute='compute_red')
	orange = fields.Boolean('orange', compute='compute_orange')
	yellow = fields.Boolean('yellow', compute='compute_yellow')
	sky = fields.Boolean('sky', compute='compute_sky')
	purple = fields.Boolean('purple', compute='compute_purple')
	pink = fields.Boolean('pink', compute='compute_pink')
	medium_blue = fields.Boolean('medium blue', compute='compute_medium_blue')
	blue = fields.Boolean('blue', compute='compute_blue')
	fushia = fields.Boolean('fushia', compute='compute_fushia')
	green = fields.Boolean('green', compute='compute_green')
	light_purple = fields.Boolean('light purple', compute='compute_light_purple')

	@api.depends('loyalty_history_ids', 'loyalty_history_ids.state', 'loyalty_history_ids.points',
				 'loyalty_history_ids.transaction_type')
	def _compute_loyalty_pts(self):
		for rec in self:
			rec.loyalty_pts = 0
			for history in rec.loyalty_history_ids:
				if history.state == 'done' and history.transaction_type == 'credit':
					rec.loyalty_pts += history.points
				if history.state == 'done' and history.transaction_type == 'debit':
					rec.loyalty_pts -= history.points

	def compute_red(self):
		is_set = False
		if self.tier_id:
			if self.ribbon_color and self.ribbon_text:
				if self.ribbon_color == 1:
					is_set = True
		self.write({'red': is_set})

	def compute_orange(self):
		is_set = False
		if self.tier_id:
			if self.ribbon_color and self.ribbon_text:
				if self.ribbon_color == 2:
					is_set = True
		self.write({'orange': is_set})

	def compute_yellow(self):
		is_set = False
		if self.tier_id:
			if self.ribbon_color and self.ribbon_text:
				if self.ribbon_color == 3:
					is_set = True
		self.write({'yellow': is_set})

	def compute_sky(self):
		is_set = False
		if self.tier_id:
			if self.ribbon_color and self.ribbon_text:
				if self.ribbon_color == 4:
					is_set = True
		self.write({'sky': is_set})

	def compute_purple(self):
		is_set = False
		if self.tier_id:
			if self.ribbon_color and self.ribbon_text:
				if self.ribbon_color == 5:
					is_set = True
		self.write({'purple': is_set})

	def compute_pink(self):
		is_set = False
		if self.tier_id:
			if self.ribbon_color and self.ribbon_text:
				if self.ribbon_color == 6:
					is_set = True
		self.write({'pink': is_set})

	def compute_medium_blue(self):
		is_set = False
		if self.tier_id:
			if self.ribbon_color and self.ribbon_text:
				if self.ribbon_color == 7:
					is_set = True
		self.write({'medium_blue': is_set})

	def compute_blue(self):
		is_set = False
		if self.tier_id:
			if self.ribbon_color and self.ribbon_text:
				if self.ribbon_color == 8:
					is_set = True
		self.write({'blue': is_set})

	def compute_fushia(self):
		is_set = False
		if self.tier_id:
			if self.ribbon_color and self.ribbon_text:
				if self.ribbon_color == 9:
					is_set = True
		self.write({'fushia': is_set})

	def compute_green(self):
		is_set = False
		if self.tier_id:
			if self.ribbon_color and self.ribbon_text:
				if self.ribbon_color == 10:
					is_set = True
		self.write({'green': is_set})

	def compute_light_purple(self):
		is_set = False
		if self.tier_id:
			if self.ribbon_color and self.ribbon_text:
				if self.ribbon_color == 11:
					is_set = True
		self.write({'light_purple': is_set})

	def update_total_sale(self):
		for record in self:
			sale_id = self.env['sale.order'].search([('partner_id', '=', record.id),('invoice_status', '=', 'invoiced')])
			pos_id = self.env['pos.order'].search([('partner_id', '=', record.id)])
			total_sale = 0
			if sale_id:
				for order in sale_id:
					for invoice in order.invoice_ids:
						if invoice.payment_state == 'paid':
							total_sale += order.amount_total
			if pos_id:
				total_sale += sum(order.amount_total for order in pos_id)
			record.total_sales = total_sale

	@api.model_create_multi
	def create(self, vals):
		result = super(resPartner, self).create(vals)
		tier_id = self.env['loyalty.tier.config'].search([('default', '=', True)], limit=1)
		if tier_id:
			result.write({'tier_id': tier_id.id})
		if self.env.user.company_id.sign_up_bonus:
			vals = {
				'partner_id': result.id,
				'points': self.env.user.company_id.sign_up_bonus,
				'state': 'done',
				'transaction_type': 'credit'
			}
			self.env['all.loyalty.history'].create(vals)
		return result
	
	def update_partner_tier(self,tier_id):
		self.update({'tier_id':tier_id})

		return tier_id
		


class allLoyaltySetting(models.Model):
	_inherit = 'all.loyalty.setting'

	loyalty_tier = fields.Many2one('loyalty.tier.config', 'Loyalty Tier')
	max_range = fields.Integer('Max Range', related='loyalty_tier.max_range')
	min_range = fields.Integer('Min Range', related='loyalty_tier.min_range')

	@api.constrains('issue_date', 'expiry_date', 'active')
	def check_date(self):
		pass

	@api.model_create_multi
	def create(self, vals):
		result = super(allLoyaltySetting, self).create(vals)
		if result.loyalty_tier:
			config = self.env['all.loyalty.setting'].sudo().search(
				[('active', '=', True), ('loyalty_tier', '=', result.loyalty_tier.id)])
			if len(config) > 1:
				msg = _("You can not apply same tier in two Loyalty Configuration!")
				raise ValidationError(msg)

		return result


class webRedeemRule(models.Model):
	_inherit = 'all.redeem.rule'

	points_redeem = fields.Integer('Minimum Points', default=1)


class webLoyaltyHistory(models.Model):
	_inherit = 'all.loyalty.history'

	loyality_id = fields.Many2one('all.loyalty.setting', 'Loyalty ID')
	credit_value = fields.Float('Credit Value', compute='_compute_credit_value')

	def _compute_credit_value(self):
		credit_value = 0
		today_date = datetime.today().date()
		for record in self:
			if record.partner_id.tier_id:
				config = self.env['all.loyalty.setting'].sudo().search(
					[('active', '=', True), ('issue_date', '<=', today_date),
					 ('expiry_date', '>=', today_date), ('loyalty_tier', '=', record.partner_id.tier_id.id)], limit=1)
				if config:
					for rule in config.redeem_ids:
						if rule.min_amt <= record.points and record.points <= rule.max_amt:
							credit_value = record.points * (rule.reward_amt / rule.points_redeem)

			record.write({'credit_value': credit_value})


class loyaltyTierConfiguration(models.Model):
	_name = 'loyalty.tier.config'
	_description = 'Loyalty Tier Configuration'
	_rec_name = 'tier_name'

	tier_name = fields.Char('Name')
	min_range = fields.Integer('Minimum Range')
	max_range = fields.Integer('Maximum Range')
	default = fields.Boolean('Default')
	ribbon_color = fields.Integer('Ribbon Color')
	ribbon_text = fields.Char('Ribbon Text')

	@api.onchange('default')
	def _check_default_box(self):
		tier_id = self.search([('default', '=', self.default)])
		for rec in tier_id:
			if rec.default == True:
				raise ValidationError("Default tier used only for one user")
