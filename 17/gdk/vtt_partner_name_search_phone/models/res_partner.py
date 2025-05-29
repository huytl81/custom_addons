# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if name:
            name_split = name.split(' / ')[-1]
            # domain = [('name', operator, name_split)] + domain

            domain = expression.AND([
                domain,
                expression.OR([
                    [('name', operator, name_split)],
                    [('phone', operator, name)],
                    [('mobile', operator, name)],
                    [('vat', operator, name)]
                ])
            ])
        # return super()._name_search(name=name, domain=domain, operator=operator, limit=limit, order=order)
        return self._search(domain, limit=limit, order=order)