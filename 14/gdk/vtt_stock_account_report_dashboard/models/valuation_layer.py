# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    categ_id = fields.Many2one(store=True)