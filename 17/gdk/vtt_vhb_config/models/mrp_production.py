# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def _get_default_date_material_deadline(self):
        if self.env.context.get('default_date_deadline'):
            return fields.Date.to_date(self.env.context.get('default_date_deadline'))
        return date.today()

    date_material_deadline = fields.Date('Material Deadline', default=_get_default_date_material_deadline)

    def action_apply_material_deadline(self):
        for mo in self:
            if mo.date_material_deadline:
                mo.move_raw_ids.date_material_deadline = mo.date_material_deadline

    def action_confirm(self):
        res = super(MRPProduction, self).action_confirm()
        if res:
            self.action_apply_material_deadline()
        return res