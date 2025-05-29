# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def action_inventory_report(self):
        context = {}
        if ("default_product_id" in self.env.context):
            context['product_id'] = self.env.context["default_product_id"]
        elif ("default_product_tmpl_id" in self.env.context):
            context['product_tmpl_id'] = self.env.context["default_product_tmpl_id"]

        return {
            "res_model": "vtt.inventory.history.wz",
            "views": [[False, "form"]],
            "target": "new",
            "type": "ir.actions.act_window",
            "context": context,
        }