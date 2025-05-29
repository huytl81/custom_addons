# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class LandTomb(models.Model):
    _name = 'vtt.land.tomb'
    _description = 'Land Tomb'

    name = fields.Char('Name')
    internal_ref = fields.Char('Ref.')
    place = fields.Char('Place')

    plot_id = fields.Many2one('vtt.land.plot', 'Plot')

    construct_ids = fields.One2many('vtt.construct', 'tomb_id', 'Construction')
    slot_ids = fields.One2many('vtt.land.tomb.slot', 'tomb_id', 'Slots')
    slot_count = fields.Integer('Slot Count', compute='_compute_slot_count')

    def _compute_slot_count(self):
        for t in self:
            t.slot_count = len(t.slot_ids)

    construct_state_simple = fields.Char('Short Construct State')