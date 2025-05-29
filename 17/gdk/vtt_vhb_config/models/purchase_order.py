# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    vtt_amount_to_invoice = fields.Monetary('Amount To Invoice', compute='_compute_amount_to_invoice', readonly=True, store=True)

    @api.depends('state', 'order_line.state', 'order_line.qty_to_invoice', 'order_line.vtt_amount_to_invoice')
    def _compute_amount_to_invoice(self):
        for po in self:
            po.vtt_amount_to_invoice = sum(po.order_line.mapped('vtt_amount_to_invoice'))