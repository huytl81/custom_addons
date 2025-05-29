# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    seat_count = fields.Integer('Seat Count', default=1)