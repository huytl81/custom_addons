# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    partner_street = fields.Char('Address', related='partner_id.street')

    ref_sale_id = fields.Many2one('sale.order', 'Ref Order')


class StockMove(models.Model):
    _inherit = 'stock.move'

    vtt_return_line_id = fields.Many2one('vtt.sale.order.return.line', 'Return Line')