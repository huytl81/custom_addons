# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.tools.misc import format_datetime


class InventoryHistoryWizard(models.TransientModel):
    _name = 'vtt.inventory.history.wz'
    _description = 'Inventory History Wizard'

    date_from = fields.Datetime('From')
    date_to = fields.Datetime('To')

    def open_at_date(self):
        tree_view_id = self.env.ref('vtt_inventory_report.vtt_view_tree_product_inventory_report').id
        form_view_id = self.env.ref('stock.product_form_view_procurement_button').id
        domain = [('type', '=', 'product')]
        product_id = self.env.context.get('product_id', False)
        product_tmpl_id = self.env.context.get('product_tmpl_id', False)
        if product_id:
            domain = expression.AND([domain, [('id', '=', product_id)]])
        elif product_tmpl_id:
            domain = expression.AND([domain, [('product_tmpl_id', '=', product_tmpl_id)]])
        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree')],
            'view_mode': 'tree,form',
            'name': f'{format_datetime(self.env, self.date_from)} - {format_datetime(self.env, self.date_to)}',
            'res_model': 'product.product',
            'domain': domain,
            'context': dict(self.env.context, to_date=self.date_to, from_date=self.date_from,
                            search_default_filter_period_stand=1),
        }
        return action