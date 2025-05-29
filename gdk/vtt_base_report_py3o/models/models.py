# -*- coding: utf-8 -*-

from odoo import models, api
TTYPE_VALID = {'char', 'date', 'datetime', 'float', 'integer', 'selection', 'text', 'html', 'monetary'}


class BaseModel(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def get_py3o_report_data(self):
        fs = self.fields_get()
        lst_f = [n for n in fs if fs[n]['type'] in TTYPE_VALID]
        data = {
            f_name: self[f_name] and self[f_name] or '' for f_name in lst_f
        }
        return data
