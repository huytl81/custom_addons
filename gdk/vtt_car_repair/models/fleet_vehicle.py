# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    def _compute_car_repair_order(self):
        for vehicle in self:
            vehicle.repair_order_count = self.env['vtt.car.repair.order'].search_count([('vehicle_id', '=', vehicle.id)])

    repair_order_count = fields.Integer('Repair Count', compute='_compute_car_repair_order')

    vtt_car_repair_ids = fields.One2many('vtt.car.repair.order', 'vehicle_id', 'Repair Orders')

    def action_view_repair(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('vtt_car_repair.vtt_action_car_repair_order_tree')
        if action:
            action.update(context=dict(self.env.context,
                                       default_vehicle_id=self.id,
                                       group_by=False),
                          domain=[('vehicle_id', '=', self.id)])
            return action

    vtt_dt_recent_car_repair = fields.Datetime('Recent Repair Date', compute='_compute_recent_repair_date', store=True)

    @api.depends('vtt_car_repair_ids')
    def _compute_recent_repair_date(self):
        for v in self:
            recent_date = False
            recent_repair = self.env['vtt.car.repair.order'].search([('state', '!=', 'cancel'), ('vehicle_id', '=', v.id)], order='dt_receive desc', limit=1)
            if recent_repair:
                recent_date = recent_repair.dt_receive
            v.vtt_dt_recent_car_repair = recent_date