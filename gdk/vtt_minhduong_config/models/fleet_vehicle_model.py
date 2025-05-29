# -*- coding; utf-8 -*-

from odoo import models, fields, api, _


class FleetVehicleModel(models.Model):
    _inherit = 'fleet.vehicle.model'

    vehicle_type = fields.Selection(selection_add=[
        ('motorbike', 'Motorbike')
    ], ondelete={'motorbike': lambda r: r.write({'vehicle_type': 'bike'})})