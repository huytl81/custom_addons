# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_round
from datetime import datetime


class Product(models.Model):
    _inherit = 'product.product'

    vtt_qty_date_from = fields.Float('Qty Date From', digits='Product Unit of Measure', compute='_compute_vtt_qty')
    vtt_qty_date_to = fields.Float('Qty Date To', digits='Product Unit of Measure', compute='_compute_vtt_qty')
    vtt_qty_in = fields.Float('Qty In', digits='Product Unit of Measure', compute='_compute_vtt_qty')
    vtt_qty_out = fields.Float('Qty Out', digits='Product Unit of Measure', compute='_compute_vtt_qty')
    vtt_value_in = fields.Float('Value In', digits='Product Price', compute='_compute_vtt_qty')
    vtt_value_out = fields.Float('Value Out', digits='Product Price', compute='_compute_vtt_qty')
    # Sale Value
    vtt_sale_value_out = fields.Float('Sale Value Out', digits='Product Price', compute='_compute_vtt_qty')
    vtt_price_past = fields.Float('Price Past', digits='Product Price', compute='_compute_vtt_qty')
    vtt_price_last = fields.Float('Price Last', digits='Product Price', compute='_compute_vtt_qty')
    vtt_value_last = fields.Float('Value Last', digits='Product Price', compute='_compute_vtt_qty')
    # Changed in Period
    vtt_period_changed = fields.Boolean('Changed?', compute='_compute_vtt_qty', store=True)
    vtt_period_stand = fields.Boolean('Stand?', compute='_compute_vtt_qty', store=True)

    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state')
    @api.depends_context(
        'lot_id', 'owner_id', 'package_id', 'from_date', 'to_date',
        'location', 'warehouse',
    )
    def _compute_vtt_qty(self):
        products = self.filtered(lambda p: p.type != 'service')
        res = products._compute_vtt_qty_dict(self._context.get('lot_id'), self._context.get('owner_id'),
                                             self._context.get('package_id'), self._context.get('from_date'),
                                             self._context.get('to_date'))
        for product in products:
            product.vtt_qty_date_from = res[product.id]['vtt_qty_date_from']
            product.vtt_qty_date_to = res[product.id]['vtt_qty_date_to']
            product.vtt_qty_in = res[product.id]['vtt_qty_in']
            product.vtt_qty_out = res[product.id]['vtt_qty_out']
            product.vtt_value_in = res[product.id]['vtt_value_in']
            product.vtt_value_out = res[product.id]['vtt_value_out']
            # Sale value
            product.vtt_sale_value_out = res[product.id]['vtt_sale_value_out']
            product.vtt_price_past = res[product.id]['vtt_price_past']
            product.vtt_price_last = res[product.id]['vtt_price_last']
            product.vtt_value_last = res[product.id]['vtt_value_last']
            # Changed in Period
            product.vtt_period_changed = res[product.id]['vtt_period_changed']
            product.vtt_period_stand = res[product.id]['vtt_period_stand']
        # Services need to be set with 0.0 for all quantities
        services = self - products
        services.vtt_qty_date_from = 0.0
        services.vtt_qty_date_to = 0.0
        services.vtt_qty_in = 0.0
        services.vtt_qty_out = 0.0
        services.vtt_value_in = 0.0
        services.vtt_value_out = 0.0
        services.vtt_price_past = 0.0
        services.vtt_price_last = 0.0
        services.vtt_value_last = 0.0
        services.vtt_sale_value_out = 0.0
        services.vtt_period_changed = False
        services.vtt_period_stand = False

    def _compute_vtt_qty_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
        domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
        if not from_date:
            from_date = datetime.min
        if not to_date:
            to_date = fields.Datetime.now()

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
        Valuation = self.env['stock.valuation.layer'].with_context(active_test=False)
        SaleLines = self.env['sale.order.line'].with_context(active_test=False)

        quants_res = dict((item['product_id'][0], (item['quantity'], item['reserved_quantity'])) for item in Quant.read_group(domain_quant, ['product_id', 'quantity', 'reserved_quantity'], ['product_id'], orderby='id'))

        # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
        domain_move_in_done = [('state', '=', 'done'), ('date', '>', from_date)] + domain_move_in_done
        domain_move_out_done = [('state', '=', 'done'), ('date', '>', from_date)] + domain_move_out_done
        moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))

        domain_move_in_from = [('state', '=', 'done'), ('date', '>=', from_date), ('date', '<=', to_date)] + list(domain_move_in)
        domain_move_out_from = [('state', '=', 'done'), ('date', '>=', from_date), ('date', '<=', to_date)] + list(domain_move_out)
        moves_in_from = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_from, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
        moves_out_from = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_from, ['product_id', 'product_qty'], ['product_id'], orderby='id'))

        domain_value_in = [('quantity', '>', 0.0), ('create_date', '>=', from_date), ('create_date', '<=', to_date)]
        domain_value_out = [('quantity', '<', 0.0), ('create_date', '>=', from_date), ('create_date', '<=', to_date)]
        value_in = dict((item['product_id'][0], item['value']) for item in Valuation.read_group(domain_value_in, ['product_id', 'value'], ['product_id'], orderby='id'))

        # Out by Cost
        value_out = dict((item['product_id'][0], item['value']) for item in Valuation.read_group(domain_value_out, ['product_id', 'value'], ['product_id'], orderby='id'))

        # Out by Sale Price
        Sale_MoveOut = Move.search(domain_move_out_from + [('sale_line_id', '!=', False)])
        saleline_ids = [m.sale_line_id.id for m in Sale_MoveOut]
        sale_value_out = dict((item['product_id'][0], item['price_subtotal']) for item in SaleLines.read_group([('id', 'in', saleline_ids)], ['product_id', 'price_subtotal'], ['product_id'], orderby='id'))

        # Calculate Cost
        domain_cost_past = [('create_date', '<=', from_date)]
        domain_cost_last = [('create_date', '<=', to_date)]
        cost_past = dict((item['product_id'][0], (item['value'], item['quantity'])) for item in Valuation.read_group(domain_cost_past, ['product_id', 'value', 'quantity'], ['product_id'], limit=1, orderby='create_date desc'))
        cost_last = dict((item['product_id'][0], (item['value'], item['quantity'])) for item in
                         Valuation.read_group(domain_cost_last, ['product_id', 'value', 'quantity'], ['product_id'], orderby='create_date desc'))

        # Calculate Value Last
        # Remove domain create_date from_date to fix bug value
        value_last = dict((item['product_id'][0], item['value']) for item in Valuation.read_group([('create_date', '<=', to_date)], ['product_id', 'value'], ['product_id'], orderby='id'))

        res = dict()
        for product in self.with_context(prefetch_fields=False):
            product_id = product.id
            if not product_id:
                res[product_id] = dict.fromkeys(
                    ['vtt_qty_date_from', 'vtt_qty_date_to', 'vtt_qty_in', 'vtt_qty_out', 'vtt_value_in', 'vtt_value_out',
                     'vtt_sale_value_out', 'vtt_price_past', 'vtt_price_last', 'vtt_value_last',
                     'vtt_period_stand', 'vtt_period_changed'],
                    0.0,
                )
                continue
            rounding = product.uom_id.rounding
            res[product_id] = {}
            qty_available = quants_res.get(product_id, [0.0])[0] - moves_in_res_past.get(product_id, 0.0) + moves_out_res_past.get(product_id, 0.0)
            res[product_id]['vtt_qty_date_from'] = float_round(qty_available, precision_rounding=rounding)
            dif = moves_in_from.get(product_id, 0.0) - moves_out_from.get(product_id, 0.0)
            res[product_id]['vtt_qty_date_to'] = float_round(qty_available + dif, precision_rounding=rounding)
            if res[product_id]['vtt_qty_date_to'] > 0.0:
                res[product_id]['vtt_period_stand'] = True
            else:
                res[product_id]['vtt_period_stand'] = False
            res[product_id]['vtt_qty_in'] = float_round(moves_in_from.get(product_id, 0.0), precision_rounding=rounding)
            res[product_id]['vtt_qty_out'] = float_round(moves_out_from.get(product_id, 0.0), precision_rounding=rounding)
            if res[product_id]['vtt_qty_in'] > 0.0 or res[product_id]['vtt_qty_out'] > 0.0:
                res[product_id]['vtt_period_changed'] = True
            else:
                res[product_id]['vtt_period_changed'] = False
            res[product_id]['vtt_value_in'] = float_round(value_in.get(product_id, 0.0), precision_rounding=1.0)
            res[product_id]['vtt_value_out'] = abs(float_round(value_out.get(product_id, 0.0), precision_rounding=1.0))
            res[product_id]['vtt_sale_value_out'] = float_round(sale_value_out.get(product_id, 0.0), precision_rounding=1.0)
            product_cost_past = cost_past.get(product_id, (0.0, 1.0))
            product_cost_last = cost_last.get(product_id, (0.0, 1.0))
            if product_cost_past[1] == 0.0:
                product_cost_past = (0.0, 1.0)
            if product_cost_last[1] == 0.0:
                product_cost_last = (0.0, 1.0)
            res[product_id]['vtt_price_past'] = float_round(product_cost_past[0] / product_cost_past[1], precision_rounding=1.0)
            res[product_id]['vtt_price_last'] = float_round(product_cost_last[0] / product_cost_last[1], precision_rounding=1.0)
            # Calculate Value Last by Standard Price
            res[product_id]['vtt_value_last'] = float_round(value_last.get(product_id, 0.0), precision_rounding=1.0)

        return res