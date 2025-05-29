# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv import expression


class UoM(models.Model):
    _inherit = 'uom.uom'

    code = fields.Char('Code')

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)',
         'This code is already used in other Unit of Measure, please choose a unique one')
    ]

    # def name_get(self):
    #     result = []
    #     for record in self:
    #         code = record.code and f'[{record.code}] ' or ''
    #         result.append((record.id, f'{code}{record.name}'))
    #     return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name.split(' ')[0] + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)