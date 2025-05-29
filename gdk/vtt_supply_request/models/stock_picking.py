# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    req_id = fields.Many2one('vtt.supply.request', 'Supply Request')