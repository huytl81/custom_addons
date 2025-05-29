# -*- coding:utf-8 -*-

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    repair_order_line_ids = fields.Many2many(
        'vtt.repair.order.line',
        'repair_order_line_invoice_rel',
        'invoice_line_id', 'repair_order_line_id',
        string='Repair Order Lines', readonly=True, copy=False)