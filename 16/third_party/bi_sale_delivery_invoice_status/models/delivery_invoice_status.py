# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class inherit_sale(models.Model):
	_inherit = "sale.order"


	is_partially_delivery = fields.Boolean(string="Partially Delivered",readonly=1,copy=False)
	is_fully_delivery = fields.Boolean(string="Fully Delivered",readonly=1,copy=False)
	is_partially_paid = fields.Boolean(string="Partially Paid",readonly=1,copy=False)
	is_fully_paid = fields.Boolean(string="Fully Paid",readonly=1,copy=False)



class inherit_stock_picking(models.Model):
	_inherit = "stock.picking"


	is_pick = fields.Boolean(string="Is Picking",compute="_compute_sale_fully_picking",store=True)


	@api.depends("move_ids_without_package.quantity_done")
	def _compute_sale_fully_picking(self):
		
		for i in self:
			sale_order = i.env['sale.order'].search([])
			for order in sale_order:
				if order.name == i.origin:
					counter_qty = 0.0
					main_qty = 0.0
					for ids in  order.picking_ids:
						for lines in ids.move_ids_without_package:
							counter_qty += lines.quantity_done

					for main in order.order_line:
						main_qty += main.product_uom_qty

					if counter_qty > 0 and i.state == 'done':
						if counter_qty < main_qty:
							order.write({
								"is_partially_delivery":True
									})

					if counter_qty == main_qty:
						order.write({
							"is_fully_delivery":True,
							"is_partially_delivery":False
								})
					i.is_pick = True 


class inherit_invoicing(models.Model):
	_inherit = "account.move"


	iss_invoice = fields.Boolean(string="Is Invoice", compute="_compute_sale_invoice" ,store=True)


	@api.depends("amount_residual")
	def _compute_sale_invoice(self):
		for invoice in self:
			sale_order = self.env['sale.order'].search([])
			for sale in sale_order:
				if sale.name == invoice.invoice_origin:
					if invoice.payment_state in ("paid", "partial"):
						sale.write({
							"is_partially_paid": True,
							"is_fully_paid": False
						})

						amount = 0
						for record in sale.invoice_ids:
							if record.payment_state in ("paid", "partial") and invoice.amount_residual == 0 and record.amount_residual == 0:
								if record.move_type in ('out_refund'):
									amount -= record.amount_total
								else:
									amount += record.amount_total

						if amount == sale.amount_total:
							sale.write({
								"is_partially_paid": False,
								"is_fully_paid": True
							})
					invoice.iss_invoice = True


