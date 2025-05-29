# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VttCustomRatingMixin(models.AbstractModel):
    _name = 'vtt.custom.rating.mixin'
    _description = 'Custom Rating Mixin'

    vtt_custom_rating_count = fields.Integer('Custom Rating Count', compute='_compute_custom_rating_count')
    vtt_custom_rating_ids = fields.One2many('vtt.custom.rating', 'record_id', 'Custom Ratings')

    def _compute_custom_rating_count(self):
        for rd in self:
            rd.vtt_custom_rating_count = len(rd.vtt_custom_rating_ids)

    def _get_custom_rating_context(self):
        self.ensure_one()
        model = self._name
        record_id = self.id
        context = {
            'default_model': model,
            'default_record_id': record_id
        }
        return context

    def submit_custom_rating(self):
        self.ensure_one()
        context = self._get_custom_rating_context()
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Rating'),
            'res_model': 'vtt.custom.rating.wz',
            'target': 'new',
            'view_mode': 'form',
            'context': context
        }
        return action

    def view_rating_data(self):
        domain = [('id', 'in', self.vtt_custom_rating_ids.ids)]
        context = self._get_custom_rating_context()
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Rating Data'),
            'res_model': 'vtt.custom.rating',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': context
        }
        return action