# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    has_state_edit_groups = fields.Boolean('State Edit Rights', compute='_compute_has_state_edit_groups')

    def _compute_has_state_edit_groups(self):
        # user = self.env.user
        if self.user_has_groups('fleet.fleet_group_manager'):
            self.has_state_edit_groups = True
        else:
            self.has_state_edit_groups = False