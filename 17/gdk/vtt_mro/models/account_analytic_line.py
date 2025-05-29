# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    repair_order_line_id = fields.Many2one('vtt.repair.order.line', string='Repair Order Item')
    repair_order_id = fields.Many2one('vtt.repair.order', 'Repair Order')

    @api.onchange('user_id')
    def onchange_user_repair_order(self):
        if self.repair_order_id and self.user_id:
            self.partner_id = self.user_id.partner_id.id