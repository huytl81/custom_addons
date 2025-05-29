# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import random


class StockLocation(models.Model):
    _inherit = 'stock.location'
    _order = 'sequence, complete_name, id'

    vtt_quants_sum = fields.Float('Total Quant Sum', compute='_compute_total_quant_sum', store=True)
    target_product_onhand = fields.Boolean(compute='_compute_target_product_onhand',
                                           search='_value_search_target_product_onhand')

    vtt_tag_ids = fields.Many2many('vtt.stock.location.tag', string='Tag')

    sequence = fields.Integer('Sequence', default=10)

    @api.depends('quant_ids', 'quant_ids.quantity')
    def _compute_total_quant_sum(self):
        for loc in self:
            quant_sum = 0.0
            for q in loc.quant_ids:
                quant_sum += q.quantity
            loc.vtt_quants_sum = quant_sum

    def _compute_target_product_onhand(self):
        context = self.env.context
        if context.get('target_product'):
            product_id = self.env['product.product'].browse(context.get('target_product'))
            quants = self.env['stock.quant'].search([('product_id', '=', product_id.id)])
            quant_locs = quants.filtered(lambda q: q.quantity > 0 and q.location_id.usage == 'internal').location_id
            for loc in self:
                if loc in quant_locs:
                    loc.target_product_onhand = True
                else:
                    loc.target_product_onhand = False
        else:
            for loc in self:
                loc.target_product_onhand = False

    @api.model
    def _value_search_target_product_onhand(self, operator, value):
        recs = self.search([]).filtered(lambda x: x.target_product_onhand is True)

        return [('id', 'in', [x.id for x in recs])]

    def action_create_internal_transfer(self):
        self.ensure_one()
        company_id = self.company_id.id
        context = self._context
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'internal'), ('warehouse_id.company_id', '=', company_id)])
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'internal'), ('warehouse_id', '=', False)])
        picking_type_id = picking_type[:1]
        move_in = context.get('loc_move_type', 'move_out')
        if move_in == 'move_in':
            loc_id = picking_type_id.default_location_dest_id.id
            loc_dest_id = self._origin.id
        else:
            loc_id = self._origin.id
            loc_dest_id = picking_type_id.default_location_dest_id.id
        # Need to upgrade to set default location for bypass the onchange picking_type_id method
        picking_vals = {
            'default_picking_type_id': picking_type_id.id,
            'default_location_id': loc_id,
            'location_id': loc_id,
            'default_location_dest_id': loc_dest_id,
            'location_dest_id': loc_dest_id,
        }
        quants = self.quant_ids.filtered(lambda q: q.quantity > 0)
        loc_products = quants.mapped('product_id')
        loc_products_data = {p: quants.filtered(lambda q: q.product_id == p) for p in loc_products}
        move_lines = []
        for p in loc_products_data:
            move_vals = {
                'name': p.name,
                'product_id': p.id,
                'product_uom': p.uom_id.id,
                'location_id': loc_id,
                'location_dest_id': loc_dest_id,
            }
            qty = sum([q.quantity for q in loc_products_data[p]])
            move_vals['product_uom_qty'] = qty
            move_vals['move_line_ids'] = [(0, 0, {
                'product_id': p.id,
                'product_uom_id': p.uom_id.id,
                'location_id': loc_id,
                'location_dest_id': loc_dest_id,
                'lot_id': q.lot_id.id,
            }) for q in loc_products_data[p]]
            move_lines.append((0, 0, move_vals))

        picking_vals['default_move_lines'] = move_lines
        action['context'] = picking_vals
        action['view_mode'] = 'form'
        action['views'] = [[False, 'form']]
        action['res_id'] = False
        return action


class StockLocationTag(models.Model):
    _name = 'vtt.stock.location.tag'
    _description = 'Stock Location Tag'

    def _get_default_color(self):
        return random.randint(1, 11)

    name = fields.Char('Name', required=True, translate=True)
    color = fields.Integer('Color Index', default=lambda self: self._get_default_color())