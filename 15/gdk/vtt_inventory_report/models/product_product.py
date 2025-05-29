# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_round


class ProductProduct(models.Model):
    _inherit = 'product.product'

    vtt_qty_date_from = fields.Float('Qty Date From', digits='Product Unit of Measure', compute='_compute_vtt_qty')
    vtt_qty_date_to = fields.Float('Qty Date To', digits='Product Unit of Measure', compute='_compute_vtt_qty')
    vtt_qty_in = fields.Float('Qty In', digits='Product Unit of Measure', compute='_compute_vtt_qty')
    vtt_qty_out = fields.Float('Qty Out', digits='Product Unit of Measure', compute='_compute_vtt_qty')

    vtt_amount_standard = fields.Float('Amount Standard', digits='Product Price', compute='_compute_vtt_qty')
    vtt_amount_list = fields.Float('Amount List Price', digits='Product Price', compute='_compute_vtt_qty')

    vtt_period_changed = fields.Boolean('Changed?', compute='_compute_vtt_qty', store=True)
    vtt_period_stand = fields.Boolean('Stand?', compute='_compute_vtt_qty', store=True)

    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state')
    @api.depends_context(
        'lot_id', 'owner_id', 'package_id', 'from_date', 'to_date',
        'location', 'warehouse',
    )
    def _compute_vtt_qty(self):
        products = self.filtered(lambda p: p.type != 'service')
        res = products._compute_vtt_qty_dict(
            self._context.get('lot_id'),
            self._context.get('owner_id'),
            self._context.get('package_id'),
            self._context.get('from_date'),
            self._context.get('to_date')
        )
        for product in products:
            product.vtt_qty_date_from = res[product.id]['vtt_qty_date_from']
            product.vtt_qty_date_to = res[product.id]['vtt_qty_date_to']
            product.vtt_qty_in = res[product.id]['vtt_qty_in']
            product.vtt_qty_out = res[product.id]['vtt_qty_out']
            product.vtt_period_changed = res[product.id]['vtt_period_changed']
            product.vtt_period_stand = res[product.id]['vtt_period_stand']
            # Amount
            product.vtt_amount_standard = res[product.id]['vtt_amount_standard']
            product.vtt_amount_list = res[product.id]['vtt_amount_list']
        services = self - products
        services.vtt_qty_date_from = 0.0
        services.vtt_qty_date_to = 0.0
        services.vtt_qty_in = 0.0
        services.vtt_qty_out = 0.0
        services.vtt_period_changed = False
        services.vtt_period_stand = False
        # Amount
        services.vtt_amount_standard = 0
        services.vtt_amount_list = 0

    def _compute_vtt_qty_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
        domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc

        domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
        domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
        if lot_id is not None:
            domain_quant += [('lot_id', '=', lot_id)]
        if owner_id is not None:
            domain_quant += [('owner_id', '=', owner_id)]
            domain_move_in += [('restrict_partner_id', '=', owner_id)]
            domain_move_out += [('restrict_partner_id', '=', owner_id)]
        if package_id is not None:
            domain_quant += [('package_id', '=', package_id)]
        domain_move_in_done = list(domain_move_in)
        domain_move_out_done = list(domain_move_out)

        Move = self.env['stock.move'].with_context(active_test=False)
        Quant = self.env['stock.quant'].with_context(active_test=False)

        # Current Quant
        quants_res = dict((item['product_id'][0], (item['quantity'], item['reserved_quantity'])) for item in
                          Quant.read_group(domain_quant, ['product_id', 'quantity', 'reserved_quantity'],
                                           ['product_id'], orderby='id'))

        # Get from_date Quant for Start period report
        domain_move_in_done = [('state', '=', 'done'), ('date', '>', from_date)] + domain_move_in_done
        domain_move_out_done = [('state', '=', 'done'), ('date', '>', from_date)] + domain_move_out_done
        moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in
                                 Move.read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id'],
                                                 orderby='id'))
        moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in
                                  Move.read_group(domain_move_out_done, ['product_id', 'product_qty'], ['product_id'],
                                                  orderby='id'))

        # Get in/ out Move in period
        domain_move_in_from = [('state', '=', 'done'), ('date', '>=', from_date), ('date', '<=', to_date)] + list(
            domain_move_in)
        domain_move_out_from = [('state', '=', 'done'), ('date', '>=', from_date), ('date', '<=', to_date)] + list(
            domain_move_out)
        moves_in_from = dict((item['product_id'][0], item['product_qty']) for item in
                             Move.read_group(domain_move_in_from, ['product_id', 'product_qty'], ['product_id'],
                                             orderby='id'))
        moves_out_from = dict((item['product_id'][0], item['product_qty']) for item in
                              Move.read_group(domain_move_out_from, ['product_id', 'product_qty'], ['product_id'],
                                              orderby='id'))

        res = dict()
        for product in self.with_context(prefetch_fields=False):
            product_id = product.id
            if not product_id:
                # res[product_id] = dict.fromkeys(
                #     ['vtt_qty_date_from', 'vtt_qty_date_to', 'vtt_qty_in', 'vtt_qty_out',],
                #     0.0,
                # )
                # res[product_id]['vtt_period_stand'] = False
                # res[product_id]['vtt_period_changed'] = False

                res[product_id] = {
                    'vtt_qty_date_from': 0.0,
                    'vtt_qty_date_to': 0.0,
                    'vtt_qty_in': 0.0,
                    'vtt_qty_out': 0.0,
                    'vtt_period_stand': False,
                    'vtt_period_changed': False,
                    'vtt_amount_standard': 0.0,
                    'vtt_amount_list': 0.0,
                }

                continue
            rounding = product.uom_id.rounding
            res[product_id] = {}
            qty_available = quants_res.get(product_id, [0.0])[0] - moves_in_res_past.get(product_id, 0.0) \
                            + moves_out_res_past.get(product_id, 0.0)

            res[product_id]['vtt_qty_date_from'] = float_round(qty_available, precision_rounding=rounding)
            dif = moves_in_from.get(product_id, 0.0) - moves_out_from.get(product_id, 0.0)
            res[product_id]['vtt_qty_date_to'] = float_round(qty_available + dif, precision_rounding=rounding)
            res[product_id]['vtt_period_stand'] = res[product_id]['vtt_qty_date_to'] > 0.0

            res[product_id]['vtt_qty_in'] = float_round(moves_in_from.get(product_id, 0.0), precision_rounding=rounding)
            res[product_id]['vtt_qty_out'] = float_round(moves_out_from.get(product_id, 0.0), precision_rounding=rounding)
            res[product_id]['vtt_period_changed'] = res[product_id]['vtt_qty_in'] > 0.0 or res[product_id]['vtt_qty_out'] > 0.0

            # Amount
            res[product_id]['vtt_amount_standard'] = res[product_id]['vtt_qty_date_to'] * product.standard_price
            res[product_id]['vtt_amount_list'] = res[product_id]['vtt_qty_date_to'] * product.list_price

        return res