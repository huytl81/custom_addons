# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    partner_street = fields.Char('Partner Street', related='picking_id.partner_id.street')
    partner_vat = fields.Char('Tax ID', related='picking_id.partner_id.vat')
    partner_ref = fields.Char('Partner Ref', related='picking_id.partner_id.ref')

    product_category_id = fields.Many2one(string='Product Category', related='product_id.categ_id', store=True)
    product_default_code = fields.Char('Default Code', related='product_id.default_code')

    warehouse_id = fields.Many2one(string='Warehouse', related='location_id.warehouse_id')
    warehouse_code = fields.Char(string='Warehouse Code', related='location_id.warehouse_id.code')
    warehouse_dest_id = fields.Many2one(string='Warehouse Destination', related='location_dest_id.warehouse_id')
    warehouse_dest_code = fields.Char(string='Warehouse Destination Code', related='location_dest_id.warehouse_id.code')

    def apply_lot_name(self):
        for sml in self:
            if sml.lot_name and not sml.lot_id:
                lots = self.env['stock.lot'].search([('product_id', '=', sml.product_id.id),
                                                     ('name', '=', sml.lot_name),
                                                     ('company_id', '=', sml.company_id.id)])
                if lots:
                    sml.lot_id = lots[0].id