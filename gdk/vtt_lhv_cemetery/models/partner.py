# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date


class ResPartner(models.Model):
    _inherit = 'res.partner'

    dob = fields.Date('Birthday')
    dod = fields.Date('Dead day')
    age = fields.Integer('Age', compute='_compute_age', store=True)

    @api.depends('dob', 'dod')
    def _compute_age(self):
        for p in self:
            age = 0
            if p.dob:
                if p.dod:
                    age = p.dod.year - p.dob.year
                else:
                    age = date.today().year - p.dob.year
            p.age = age

    life_state = fields.Selection([
        ('alive', 'Alive'),
        ('dead', 'Dead')
    ], 'Life State', default='alive')

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], 'Gender', default='male', required=True)

    def action_view_rated_data(self):
        domain = [('partner_id', '=', self.id)]
        context = {
            'default_partner_id': self.id
        }
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Rating Data'),
            'res_model': 'vtt.custom.rating',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': context
        }
        return action