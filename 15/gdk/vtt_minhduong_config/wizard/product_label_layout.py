# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from collections import defaultdict


class ProductLabelLayout(models.TransientModel):
    _inherit = 'product.label.layout'

    print_format = fields.Selection(selection_add=[
        ('2x1', '2 x 1'),
        ('3x1', '3 x 1'),
    ], ondelete={
        '2x1': 'set default',
        '3x1': 'set default',},)

    lot_ids = fields.Many2many('stock.production.lot')
    quant_ids = fields.Many2many('stock.quant')

    report_line_ids = fields.One2many('vtt.product.label.layout.line', 'wz_id', 'Lines')

    @api.onchange('move_line_ids')
    def onchange_move_line_ids(self):
        if self.move_line_ids:
            self.report_line_ids = [(0, 0, {
                'product_id': m.product_id.id,
                'lot_name': m.lot_id and m.lot_id.name or m.lot_name,
                'expiration_date': m.expiration_date,
                'product_uom_id': m.product_uom_id.id,
                # 'print_count': self.custom_quantity,
                'print_count': m.vtt_pack_qty if m.vtt_pack_qty > 0 else 1,
            }) for m in self.move_line_ids]

    @api.onchange('lot_ids')
    def onchange_lot_ids(self):
        if self.lot_ids:
            self.product_ids = self.lot_ids.mapped('product_id')
            self.report_line_ids = [(0, 0, {
                'product_id': lot.product_id.id,
                'lot_name': lot.name,
                'expiration_date': lot.expiration_date,
                'product_uom_id': lot.product_id.uom_id.id,
                'print_count': self.custom_quantity,
            }) for lot in self.lot_ids]

    @api.onchange('quant_ids')
    def onchange_quant_ids(self):
        if self.quant_ids:
            self.lot_ids = self.quant_ids.mapped('lot_id')

    def _prepare_report_data(self):
        xml_id, data = super()._prepare_report_data()

        if self.picking_quantity == 'custom' and self.report_line_ids:
            qties = defaultdict(int)
            custom_barcodes = defaultdict(list)
            uom_unit = self.env.ref('uom.product_uom_categ_unit', raise_if_not_found=False)
            for line in self.report_line_ids:
                if line.product_uom_id.category_id == uom_unit and line.print_count:
                    custom_barcodes[line.product_id.id].append((line.lot_name, line.print_count))
                    # qties[line.product_id.id] += 1.0
                    # qties[line.product_id.id] += line.print_count

            # data['quantity_by_product'] = {p: 0 for p, q in qties.items()}
            # data['quantity_by_product'] = {p: q for p, q in qties.items()}
            data['quantity_by_product'] = {}
            data['custom_barcodes'] = custom_barcodes
        elif self.picking_quantity == 'custom' and self.lot_ids:
            qties = defaultdict(int)
            custom_barcodes = defaultdict(list)
            uom_unit = self.env.ref('uom.product_uom_categ_unit', raise_if_not_found=False)
            for lot in self.lot_ids:
                if lot.product_id.uom_id.category_id == uom_unit:
                    custom_barcodes[lot.product_id.id].append((lot.name, self.custom_quantity))
                    # qties[lot.product_id.id] += 1.0
                    # qties[lot.product_id.id] += self.custom_quantity

            # data['quantity_by_product'] = {p: 0 for p, q in qties.items()}
            # data['quantity_by_product'] = {p: q for p, q in qties.items()}
            data['quantity_by_product'] = {}
            data['custom_barcodes'] = custom_barcodes
        elif self.picking_quantity == 'custom' and self.move_line_ids:
            qties = defaultdict(int)
            custom_barcodes = defaultdict(list)
            uom_unit = self.env.ref('uom.product_uom_categ_unit', raise_if_not_found=False)
            for line in self.move_line_ids:
                if line.product_uom_id.category_id == uom_unit:
                    if (line.lot_id or line.lot_name):
                        custom_barcodes[line.product_id.id].append((line.lot_id.name or line.lot_name, self.custom_quantity))
                        continue
                    qties[line.product_id.id] += line.qty_done

            data['quantity_by_product'] = {p: self.custom_quantity for p, q in qties.items()}
            data['custom_barcodes'] = custom_barcodes

        return xml_id, data

    def action_clear_all_count(self):
        # view_id = self.env.ref('vtt_minhduong_config.vtt_view_form_product_label_layout_report_buttons')
        self.report_line_ids.print_count = 0
        return {
            'type': 'ir.actions.act_window',
            'name': _('Choose Labels Layout'),
            'view_mode': 'form',
            # 'views': [(view_id.id, 'form')],
            'res_model': self._name,
            'res_id': self.id,
            'target': 'new',
        }

    def action_set_all_count(self):
        # view_id = self.env.ref('vtt_minhduong_config.vtt_view_form_product_label_layout_report_buttons')
        self.report_line_ids.print_count = self.custom_quantity
        return {
            'type': 'ir.actions.act_window',
            'name': _('Choose Labels Layout'),
            'view_mode': 'form',
            # 'views': [(view_id.id, 'form')],
            'res_model': self._name,
            'res_id': self.id,
            'target': 'new',
        }


class ProductLabelLayoutLine(models.TransientModel):
    _name = 'vtt.product.label.layout.line'
    _description = 'Product Label Layout Line'

    wz_id = fields.Many2one('product.label.layout', 'Layout')

    product_id = fields.Many2one('product.product', 'Product')
    lot_name = fields.Char('Lot/ Serial')
    expiration_date = fields.Datetime('Expiration Date')
    product_uom_id = fields.Many2one('uom.uom', 'UoM')

    print_count = fields.Integer('Count')