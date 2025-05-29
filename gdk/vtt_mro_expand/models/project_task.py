# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def create_quotation(self):
        user = self.env.user
        for rec in self:
            if not rec.car_repair_estimation_line_ids:
                raise UserError(_('Please add Estimation detail to create quotation!'))
            vales = {
                'car_task_id': rec.id,
                'partner_id': rec.partner_id.id,
                'user_id': user.id,
                'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            }
            order_id = self.env['sale.order'].sudo().create(vales)
            for line in rec.car_repair_estimation_line_ids:

                if not line.product_id:
                    raise UserError(_('Product not defined on Estimation Repair Lines!'))

                price_unit = line.price
                if order_id.pricelist_id:
                    price_unit, rule_id = order_id.pricelist_id.get_product_price_rule(
                        line.product_id,
                        line.qty or 1.0,
                        order_id.partner_id
                    )

                orderlinevals = {
                    'order_id': order_id.id,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.qty,
                    'product_uom': line.product_uom.id,
                    'price_unit': price_unit,
                    'name': line.notes or line.product_id.description_sale or line.product_id.name,
                }
                line_id = self.env['sale.order.line'].create(orderlinevals)
        action = self.env.ref('sale.action_quotations')
        result = action.read()[0]
        result['domain'] = [('id', '=', order_id.id)]
        return result
