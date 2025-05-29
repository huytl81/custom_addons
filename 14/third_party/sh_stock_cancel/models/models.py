# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    state = fields.Selection(selection_add=[
        ('cancel', 'Cancel')])

    def action_inventory_scrap_cancel(self):
        for rec in self:
            rec.sudo().mapped('move_id').sudo().write({'state': 'cancel'})
            rec.sudo().mapped('move_id').mapped(
                'move_line_ids').sudo().write({'state': 'cancel'})
            rec._sh_unreseve_qty()
            rec.sudo().write({'state': 'cancel'})

    def action_inventory_cancel_scrap_draft(self):
        for rec in self:
            rec.sudo().mapped('move_id').sudo().write({'state': 'draft'})
            rec.sudo().mapped('move_id').mapped(
                'move_line_ids').sudo().write({'state': 'draft'})
            rec._sh_unreseve_qty()
            rec.sudo().write({'state': 'draft'})

    def action_inventory_cancel_scrap_delete(self):
        for rec in self:
            rec.sudo().mapped('move_id').sudo().write({'state': 'draft'})
            rec.sudo().mapped('move_id').mapped(
                'move_line_ids').sudo().write({'state': 'draft'})
            rec._sh_unreseve_qty()
            rec.sudo().mapped('move_id').sudo().unlink()
            rec.sudo().mapped('move_id').mapped('move_line_ids').sudo().unlink()
            rec.sudo().write({'state': 'draft'})
            rec.sudo().unlink()

    def _sh_unreseve_qty(self):
        for move_line in self.sudo().mapped('move_id').sudo().mapped('move_line_ids'):
            # unreserve qty
            quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_id.id),
                                                           ('product_id', '=',
                                                            move_line.product_id.id),
                                                           ('lot_id', '=', move_line.lot_id.id)], limit=1)

            if quant:
                quant.write({'quantity': quant.quantity + move_line.qty_done})

            quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_dest_id.id),
                                                           ('product_id', '=',
                                                            move_line.product_id.id),
                                                           ('lot_id', '=', move_line.lot_id.id)], limit=1)

            if quant:
                quant.write({'quantity': quant.quantity - move_line.qty_done})

    def sh_cancel(self):
        if self.company_id.scrap_operation_type == 'cancel':

            self.sudo().mapped('move_id').sudo().write({'state': 'cancel'})
            self.sudo().mapped('move_id').mapped(
                'move_line_ids').sudo().write({'state': 'cancel'})
            self._sh_unreseve_qty()
            self.sudo().write({'state': 'cancel'})

        elif self.company_id.scrap_operation_type == 'cancel_draft':

            self.sudo().mapped('move_id').sudo().write({'state': 'draft'})
            self.sudo().mapped('move_id').mapped(
                'move_line_ids').sudo().write({'state': 'draft'})
            self._sh_unreseve_qty()
            self.sudo().write({'state': 'draft'})

        elif self.company_id.scrap_operation_type == 'cancel_delete':

            self.sudo().mapped('move_id').sudo().write({'state': 'draft'})
            self.sudo().mapped('move_id').mapped(
                'move_line_ids').sudo().write({'state': 'draft'})
            self._sh_unreseve_qty()
            self.sudo().mapped('move_id').sudo().unlink()
            self.sudo().mapped('move_id').mapped('move_line_ids').sudo().unlink()
            self.sudo().write({'state': 'draft'})
            self.sudo().unlink()

            return {
                'name': 'Stock Scrap',
                'type': 'ir.actions.act_window',
                'res_model': 'stock.scrap',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'target': 'current',
            }


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    def action_inventory_cancel(self):
        for rec in self:
            rec.sudo().mapped('move_ids').sudo().write({'state': 'cancel'})
            rec.sudo().mapped('move_ids').mapped(
                'move_line_ids').sudo().write({'state': 'cancel'})
            rec._sh_unreseve_qty()
            rec.sudo().write({'state': 'cancel'})

    def action_inventory_cancel_draft(self):
        for rec in self:
            rec.sudo().mapped('move_ids').sudo().write({'state': 'draft'})
            rec.sudo().mapped('move_ids').mapped(
                'move_line_ids').sudo().write({'state': 'draft'})
            rec._sh_unreseve_qty()
            rec.sudo().write({'state': 'draft'})

    def action_inventory_cancel_delete(self):
        for rec in self:
            rec.sudo().mapped('move_ids').sudo().write({'state': 'draft'})
            rec.sudo().mapped('move_ids').mapped(
                'move_line_ids').sudo().write({'state': 'draft'})
            rec._sh_unreseve_qty()
            rec.sudo().mapped('move_ids').sudo().unlink()
            rec.sudo().mapped('move_ids').mapped('move_line_ids').sudo().unlink()
            rec.sudo().write({'state': 'draft'})
            rec.sudo().unlink()

    def _sh_unreseve_qty(self):
        for move_line in self.sudo().mapped('move_ids').mapped('move_line_ids'):
            # unreserve qty
            quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_id.id),
                                                           ('product_id', '=',
                                                            move_line.product_id.id),
                                                           ('lot_id', '=', move_line.lot_id.id)], limit=1)

            if quant:
                quant.write({'quantity': quant.quantity + move_line.qty_done})

            quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_dest_id.id),
                                                           ('product_id', '=',
                                                            move_line.product_id.id),
                                                           ('lot_id', '=', move_line.lot_id.id)], limit=1)

            if quant:
                quant.write({'quantity': quant.quantity - move_line.qty_done})

    def sh_cancel(self):
        if self.company_id.adj_operation_type == 'cancel':

            self.sudo().mapped('move_ids').sudo().write({'state': 'cancel'})
            self.sudo().mapped('move_ids').mapped(
                'move_line_ids').sudo().write({'state': 'cancel'})
            self._sh_unreseve_qty()
            self.sudo().write({'state': 'cancel'})

        elif self.company_id.adj_operation_type == 'cancel_draft':

            self.sudo().mapped('move_ids').sudo().write({'state': 'draft'})
            self.sudo().mapped('move_ids').mapped(
                'move_line_ids').sudo().write({'state': 'draft'})
            self._sh_unreseve_qty()
            self.sudo().write({'state': 'draft'})

        elif self.company_id.adj_operation_type == 'cancel_delete':

            self.sudo().mapped('move_ids').sudo().write({'state': 'draft'})
            self.sudo().mapped('move_ids').mapped(
                'move_line_ids').sudo().write({'state': 'draft'})
            self._sh_unreseve_qty()
            self.sudo().mapped('move_ids').sudo().unlink()
            self.sudo().mapped('move_ids').mapped('move_line_ids').sudo().unlink()
            self.sudo().write({'state': 'draft'})
            self.sudo().unlink()

            return {
                'name': 'Inventory Adjustments',
                'type': 'ir.actions.act_window',
                'res_model': 'stock.inventory',
                'view_type': 'form',
                'view_mode': 'tree,kanban,form',
                'target': 'current',
            }


class Move(models.Model):
    _inherit = 'stock.move'

    def _sh_unreseve_qty(self):
        for move_line in self.sudo().mapped('move_line_ids'):
            # unreserve qty
            quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_id.id),
                                                           ('product_id', '=',
                                                            move_line.product_id.id),
                                                           ('lot_id', '=', move_line.lot_id.id)], limit=1)

            if quant:
                quant.write({'quantity': quant.quantity + move_line.qty_done})

            quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_dest_id.id),
                                                           ('product_id', '=',
                                                            move_line.product_id.id),
                                                           ('lot_id', '=', move_line.lot_id.id)], limit=1)

            if quant:
                quant.write({'quantity': quant.quantity - move_line.qty_done})

    def action_move_cancel(self):
        for rec in self:
            rec.sudo().write({'state': 'cancel'})
            rec.mapped('move_line_ids').sudo().write({'state': 'cancel'})
            rec._sh_unreseve_qty()

    def action_move_cancel_draft(self):
        for rec in self:
            rec.sudo().write({'state': 'draft'})
            rec.mapped('move_line_ids').sudo().write({'state': 'draft'})
            rec._sh_unreseve_qty()

    def action_move_cancel_delete(self):
        for rec in self:
            rec.sudo().write({'state': 'draft'})
            rec.mapped('move_line_ids').sudo().write({'state': 'draft'})
            rec._sh_unreseve_qty()
            rec.mapped('move_line_ids').sudo().unlink()
            rec.sudo().unlink()


class Picking(models.Model):
    _inherit = 'stock.picking'

    def action_picking_cancel(self):
        for rec in self:
            if rec.sudo().mapped('move_ids_without_package'):
                rec.sudo().mapped('move_ids_without_package').sudo().write(
                    {'state': 'cancel'})
                rec.sudo().mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().write({'state': 'cancel'})
                rec._sh_unreseve_qty()
            rec.sudo().write({'state': 'cancel'})

    def action_picking_cancel_draft(self):
        for rec in self:
            if rec.sudo().mapped('move_ids_without_package'):
                rec.sudo().mapped('move_ids_without_package').sudo().write(
                    {'state': 'draft'})
                rec.sudo().mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                rec._sh_unreseve_qty()
            rec.sudo().write({'state': 'draft'})

    def action_picking_cancel_delete(self):
        for rec in self:
            if rec.sudo().mapped('move_ids_without_package'):
                rec.sudo().mapped('move_ids_without_package').sudo().write(
                    {'state': 'draft'})
                rec.sudo().mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                rec._sh_unreseve_qty()
                rec.sudo().mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().unlink()
                rec.sudo().mapped('move_ids_without_package').sudo().unlink()
            rec.sudo().write({'state': 'draft', 'show_mark_as_todo': True})
            rec.sudo().unlink()

    def _sh_unreseve_qty(self):
        for move_line in self.sudo().mapped('move_ids_without_package').mapped('move_line_ids'):
            # unreserve qty
            quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_id.id),
                                                           ('product_id', '=',
                                                            move_line.product_id.id),
                                                           ('lot_id', '=', move_line.lot_id.id)], limit=1)

            if quant:
                quant.write({'quantity': quant.quantity + move_line.qty_done})

            quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_dest_id.id),
                                                           ('product_id', '=',
                                                            move_line.product_id.id),
                                                           ('lot_id', '=', move_line.lot_id.id)], limit=1)

            if quant:
                quant.write({'quantity': quant.quantity - move_line.qty_done})

    def sh_cancel(self):

        if self.company_id.picking_operation_type == 'cancel':
            if self.sudo().mapped('move_ids_without_package'):
                self.sudo().mapped('move_ids_without_package').sudo().write(
                    {'state': 'cancel'})
                self.sudo().mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().write({'state': 'cancel'})
                self._sh_unreseve_qty()
            self.sudo().write({'state': 'cancel'})
            
        elif self.company_id.picking_operation_type == 'cancel_draft':
            if self.sudo().mapped('move_ids_without_package'):
                self.sudo().mapped('move_ids_without_package').sudo().write(
                    {'state': 'draft'})
                self.sudo().mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                self._sh_unreseve_qty()
            self.sudo().write({'state': 'draft'})

        elif self.company_id.picking_operation_type == 'cancel_delete':
            if self.sudo().mapped('move_ids_without_package'):
                self.sudo().mapped('move_ids_without_package').sudo().write(
                    {'state': 'draft'})
                self.sudo().mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().write({'state': 'draft'})
                self._sh_unreseve_qty()
                self.sudo().mapped('move_ids_without_package').mapped(
                    'move_line_ids').sudo().unlink()
                self.sudo().mapped('move_ids_without_package').sudo().unlink()
            self.sudo().write({'state': 'draft', 'show_mark_as_todo': True})
            self.sudo().unlink()
            
            return {
                'name': 'Inventory Transfer',
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'view_type': 'form',
                'view_mode': 'tree,kanban,form',
                'target': 'current',
            }
            