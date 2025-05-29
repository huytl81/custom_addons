# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    def write(self, vals):
        if 'active' in vals and not vals['active']:
            contracts = self.env['fleet.vehicle.log.contract'].search([('vehicle_id', 'in', self.ids)])
            services = self.env['fleet.vehicle.log.services'].search([('vehicle_id', 'in', self.ids)])
        else:
            contracts = False
            services = False

        res = super(FleetVehicle, self).write(vals)

        if contracts:
            contracts.active = True
        if services:
            services.active = True
        return res