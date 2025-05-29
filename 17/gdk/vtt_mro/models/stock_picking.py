# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    repair_order_id = fields.Many2one('vtt.repair.order', 'Repair Order', related="group_id.repair_order_id", store=True, index='btree_not_null')