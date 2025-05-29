# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'

    def action_pickings_print(self):
        print_context = self._context.get('picking_print_type', 'stock.action_report_delivery')
        self.ensure_one()
        pickings = self.mapped('picking_ids')
        return self.env.ref(print_context).report_action(pickings)

    picking_count = fields.Integer('Pickings Count', compute='_compute_picking_count')

    def _compute_picking_count(self):
        for pb in self:
            pb.picking_count = len(pb.picking_ids)

    def action_view_pickings_tree(self):
        self.ensure_one()
        pickings = self.mapped('picking_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        action['domain'] = [('id', 'in', pickings.ids)]
        return action