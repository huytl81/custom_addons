# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    vtt_return_line_id = fields.Many2one('vtt.sale.order.return.line', 'Return Line')