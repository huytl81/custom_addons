# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID


class VttCustomRatingWizard(models.TransientModel):
    _inherit = 'vtt.custom.rating.wz'

    def _get_default_stage_id(self):
        return self.env['vtt.custom.rating.stage'].search([('fold', '=', False),
                                                           ('is_closed', '=', False)], order='sequence', limit=1).id

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    stage_id = fields.Many2one('vtt.custom.rating.stage', string='Stage',
                               store=True, readonly=False, ondelete='restrict', index=True,
                               default=_get_default_stage_id, group_expand='_read_group_stage_ids',
                               copy=False)

    def _get_rating_vals(self):
        vals = super(VttCustomRatingWizard, self)._get_rating_vals()
        vals.update({
            'stage_id': self.stage_id.id
        })
        return vals