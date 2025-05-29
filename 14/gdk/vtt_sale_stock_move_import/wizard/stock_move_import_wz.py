# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import magic
import base64
import xlrd
from odoo.exceptions import UserError


class VttStockMoveImportWizard(models.TransientModel):
    _name = 'vtt.stock.move.import.wz'
    _description = 'Stock Move Import Wizard'

    stock_picking_id = fields.Many2one('stock.picking', 'Picking')
    sale_order_id = fields.Many2one('sale.order', 'Sale Order')

    products_file = fields.Binary('Product List', attachment=False)
    products_filename = fields.Char('Filename')

    is_update = fields.Boolean('Update Existed?', default=False)

    def action_import_product_xls(self):
        mime = magic.from_buffer(base64.decodebytes(self.products_file), mime=True)
        valid_mime = mime in [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
        ]

        if valid_mime:
            wb = xlrd.open_workbook(file_contents=base64.decodebytes(self.products_file))
            sheet = wb.sheets()[0]

            if self.sale_order_id:
                picking_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing')], limit=1)
                partner = self.sale_order_id.partner_id
                picking_vals = {
                    'picking_type_id': picking_type.id,
                    'location_id': picking_type.default_location_src_id.id,
                    'location_dest_id': partner.property_stock_customer.id,
                    'partner_id': partner.id,
                    'move_type': 'direct',
                    # 'sale_id': self.sale_order_id.id,
                    'origin': self.sale_order_id.name,
                    'vtt_special_import': True,
                }

                lst = []
                move_vals_lst = []
                for row in range(sheet.nrows):
                    if row > 0:
                        qty = sheet.cell(row, 4).value or 0.0
                        if not sheet.cell(row, 0).value or not sheet.cell(row, 3).value or not isinstance(qty, float):
                            continue
                        else:
                            lst.append((sheet.cell(row, 0).value, sheet.cell(row, 3).value, qty))
                if lst:
                    lst_code = [i[0] for i in lst]
                    lst_uom_code = [i[1] for i in lst]
                    product_templates = self.env['product.template'].search([('default_code', 'in', lst_code)])
                    products = self.env['product.product'].search([('product_tmpl_id', 'in', product_templates.ids)])
                    uoms = self.env['uom.uom'].search([('code', 'in', lst_uom_code)])

                    for l in lst:
                        product_tmpl = product_templates.filtered(lambda pt: pt.default_code == l[0])
                        product = products.filtered(lambda p: p.product_tmpl_id == product_tmpl and p.active)
                        uom = uoms.filtered(lambda u: u.active and u.code == l[1])
                        check_uom = product_tmpl.uom_id.category_id == uom.category_id
                        if product and uom and check_uom:
                            for p in product:
                                move_vals_lst.append((0, 0, {
                                    'name': p.name,
                                    'product_id': p.id,
                                    'product_uom': uom.id,
                                    'product_uom_qty': l[2],
                                    'location_id': picking_type.default_location_src_id.id,
                                    'location_dest_id': partner.property_stock_customer.id,
                                    'group_id': self.sale_order_id.procurement_group_id.id,
                                }))

                if move_vals_lst:
                    picking_vals.update({
                        'move_lines': move_vals_lst
                    })

                    self.env['stock.picking'].create(picking_vals)

            elif self.stock_picking_id:
                moves = self.stock_picking_id.move_lines
                lst = []
                move_vals_lst = []
                for row in range(sheet.nrows):
                    if row > 0:
                        qty = sheet.cell(row, 4).value or 0.0
                        if not sheet.cell(row, 0).value or not sheet.cell(row, 3).value or not isinstance(qty, float):
                            continue
                        else:
                            lst.append((sheet.cell(row, 0).value, sheet.cell(row, 3).value, qty))
                if lst:
                    lst_code = [i[0] for i in lst]
                    lst_uom_code = [i[1] for i in lst]
                    product_templates = self.env['product.template'].search([('default_code', 'in', lst_code)])
                    products = self.env['product.product'].search([('product_tmpl_id', 'in', product_templates.ids)])
                    uoms = self.env['uom.uom'].search([('code', 'in', lst_uom_code)])

                    for l in lst:
                        product_tmpl = product_templates.filtered(lambda pt: pt.default_code == l[0])
                        product = products.filtered(lambda p: p.product_tmpl_id == product_tmpl and p.active)
                        uom = uoms.filtered(lambda u: u.active and u.code == l[1])
                        check_uom = product_tmpl.uom_id.category_id == uom.category_id
                        if product and uom and check_uom:
                            if not self.is_update:
                                for p in product:
                                    move_vals_lst.append((0, 0, {
                                        'name': p.name,
                                        'product_id': p.id,
                                        'product_uom': uom.id,
                                        'product_uom_qty': l[2],
                                        'location_id': self.stock_picking_id.location_id.id,
                                        'location_dest_id': self.stock_picking_id.location_dest_id.id,
                                    }))
                            else:
                                for p in product:
                                    move = moves.filtered(lambda m: m.product_id == p)
                                    if move:
                                        move_vals_lst.append((1, move[0].id, {
                                            'product_uom': uom.id,
                                            'product_uom_qty': l[2],
                                        }))

                if move_vals_lst:
                    self.stock_picking_id.with_context(default_picking_id=self.stock_picking_id.id).write({
                        'move_lines': move_vals_lst
                    })

        else:
            raise UserError(_('The file in used is incorrect format.\n'
                              'Please checkout your file before continue.'))