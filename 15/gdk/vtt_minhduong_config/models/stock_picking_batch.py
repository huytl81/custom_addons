# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'

    vtt_fleet_vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
    vtt_fleet_driver_id = fields.Many2one('res.partner', 'Driver')

    @api.onchange('vtt_fleet_vehicle_id')
    def onchange_vtt_fleet_vehicle_id(self):
        if self.vtt_fleet_vehicle_id:
            self.vtt_fleet_driver_id = self.vtt_fleet_vehicle_id.driver_id

    def write(self, vals):
        res = super(StockPickingBatch, self).write(vals)
        lst_fields = ['vtt_fleet_vehicle_id', 'vtt_fleet_driver_id', 'picking_ids']
        if any(f in vals for f in lst_fields):
            self.picking_ids.vtt_fleet_vehicle_id = self.vtt_fleet_vehicle_id
            self.picking_ids.vtt_fleet_driver_id = self.vtt_fleet_driver_id
        return res

    def action_confirm(self):
        if self.picking_ids:
            self.picking_ids.vtt_fleet_vehicle_id = self.vtt_fleet_vehicle_id
            self.picking_ids.vtt_fleet_driver_id = self.vtt_fleet_driver_id
        return super().action_confirm()