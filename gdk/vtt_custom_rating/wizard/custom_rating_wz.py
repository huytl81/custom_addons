# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VttCustomRatingWizard(models.TransientModel):
    _name = 'vtt.custom.rating.wz'
    _description = 'Custom Rating Wizard'

    short_description = fields.Char('Short Description')
    full_description = fields.Text('Full Description')

    dt_rating = fields.Datetime('Date', default=fields.Datetime.now())
    partner_id = fields.Many2one('res.partner', 'Partner')

    # def _get_default_rating_user(self):
    #     context = self._context
    #     if context.get('default_user_id'):
    #         return self.env['res.users'].browse(context.get('default_user_id'))
    #     else:
    #         return False

    model = fields.Char('Model')
    record_id = fields.Integer('Record ID')

    rating = fields.Selection([
        ('0', 'Unhappy'),
        ('1', 'Poor'),
        ('2', 'Normal'),
        ('3', 'Fine'),
        ('4', 'Happy'),
        ('5', 'Excellent')
    ], 'Rating', default='3')

    rating_type = fields.Selection([
        ('positive', 'Positive'),
        ('negative', 'Negative')
    ], 'Type', default='positive')

    user_id = fields.Many2one('res.users', 'User')
    receive_user_id = fields.Many2one('res.users', 'Receiver', default=lambda self: self.env.user)

    def _get_rating_vals(self):
        vals = {
            'short_description': self.short_description,
            'full_description': self.full_description,
            'model': self.model,
            'record_id': self.record_id,
            'partner_id': self.partner_id.id,
            'dt_rating': self.dt_rating,
            'rating': self.rating,
            'rating_point': float(self.rating),
            'rating_type': self.rating_type,
            'receive_user_id': self.receive_user_id.id,
            'user_id': self.user_id.id
        }
        return vals

    def submit_rating(self):
        vals = self._get_rating_vals()
        new_rating = self.env['vtt.custom.rating'].create(vals)
        return new_rating