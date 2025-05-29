# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ThreatSyncMixin(models.AbstractModel):
    _name = 'threat.sync.mixin'
    _description = 'Threat Sync Mixin'

    s_id = fields.Integer('Server ID')

    def get_s_id(self):
        return {s.id: s.s_id for s in self}

    def update_s_id(self, s_id_data):
        if s_id_data:
            for s in s_id_data:
                rd = self.browse(int(s))
                rd.s_id = s_id_data[s]
