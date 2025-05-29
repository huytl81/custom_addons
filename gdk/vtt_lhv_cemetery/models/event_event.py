# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class EventEvent(models.Model):
    _inherit = 'event.event'

    image = fields.Binary('Image')

    seat_count = fields.Integer('Seat Count', compute='_compute_total_seat_count', store=True)

    @api.depends('registration_ids', 'registration_ids.state')
    def _compute_total_seat_count(self):
        for e in self:
            seat_count = 0
            for r in e.registration_ids:
                if r.state in ['open', 'done']:
                    seat_count += r.seat_count
            e.seat_count = seat_count