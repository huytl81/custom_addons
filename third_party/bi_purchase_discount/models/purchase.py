# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.tools.misc import formatLang


class purchase_order_line(models.Model):
	_inherit = 'purchase.order.line'

	discount = fields.Float('Discount %')

	def _prepare_account_move_line(self, move=False):
		result = super(purchase_order_line, self)._prepare_account_move_line()
		if result:
			result.update({
				'discount' : self.discount,
		  	})
		return result 

	def _convert_to_tax_base_line_dict(self):
		self.ensure_one()
		return self.env['account.tax']._convert_to_tax_base_line_dict(
			self,
			partner=self.order_id.partner_id,
			currency=self.order_id.currency_id,
			product=self.product_id,
			taxes=self.taxes_id,
			price_unit=self.price_unit,
			quantity=self.product_qty,
			price_subtotal=self.price_subtotal,
			discount=self.discount
		)

