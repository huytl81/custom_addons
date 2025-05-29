# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID


class VttCustomRating(models.Model):
    _inherit = 'vtt.custom.rating'

    def _get_default_stage_id(self):
        return self.env['vtt.custom.rating.stage'].search([('fold', '=', False),
                                                           ('is_closed', '=', False)], order='sequence', limit=1).id

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    stage_id = fields.Many2one('vtt.custom.rating.stage', string='Stage',
                               store=True, readonly=False, ondelete='restrict', tracking=True, index=True,
                               default=_get_default_stage_id, group_expand='_read_group_stage_ids',
                               copy=False)

    rating_comment = fields.Text('Rating Comment')


class VttCustomRatingStage(models.Model):
    _name = 'vtt.custom.rating.stage'
    _description = 'Custom Rating Stage'
    _order = 'sequence, id'

    name = fields.Char('Name', translate=True)
    description = fields.Text('Description')
    sequence = fields.Integer('Sequence', default=1)

    fold = fields.Boolean(string='Folded in Kanban')
    is_closed = fields.Boolean('Closing Stage')

    stage_message = fields.Char('Stage Message')

    type = fields.Selection([
        ('internal', 'Internal'),
        ('public', 'Public')
    ], 'Type', default='internal')

    #for mobile
    mobile_icon = fields.Char('Mobile icon')
    mobile_color = fields.Char('Mobile hex color')