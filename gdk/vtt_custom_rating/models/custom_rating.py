# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VttCustomRating(models.Model):
    _name = 'vtt.custom.rating'
    _description = 'Custom Rating'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    short_description = fields.Char('Short Description')
    full_description = fields.Text('Full Description')

    dt_rating = fields.Datetime('Date', default=fields.Datetime.now())
    partner_id = fields.Many2one('res.partner', 'Partner')

    model = fields.Char('Model', readonly=True)
    record_id = fields.Many2oneReference('Record ID', model_field='model', readonly=True)

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

    rating_point = fields.Float('Rating Point', compute='_compute_rating_point', group_operator='avg', store=True)

    @api.depends('rating')
    def _compute_rating_point(self):
        for cr in self:
            cr.rating_point = float(cr.rating)

    def name_get(self):
        result = []
        for cr in self:
            name = f'{_(cr.rating_type)} {cr.dt_rating.date()}'
            if cr.partner_id:
                name = f'{cr.partner_id.name} - ' + name
            result.append((cr.id, name))
        return result

    def view_rated_document(self):
        model = self.model
        record_id = self.record_id
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Rated Document'),
            'res_model': model,
            'target': 'new',
            'view_mode': 'form',
            'res_id': record_id.id,
        }
        return action