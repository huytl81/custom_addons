# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    req_id = fields.Many2one('vtt.supply.request', 'Supply Request')