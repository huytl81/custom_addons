# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vtt_partner_code = fields.Char('Partner Code')

    _sql_constraints = [
        ('unique_partner_code', 'UNIQUE(vtt_partner_code)', 'One Partner should only have one Partner Code.')
    ]

    @api.model
    def get_partner_by_code(self, code):
        partner = self.search([('vtt_partner_code', '=', code)], limit=1)
        return partner and partner or False

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # Domain by VAT number, Partner code
            vat_domain = ['|', '|', '|',
                          ('vat', operator, name),
                          ('vtt_partner_code', operator, name),
                          ('phone', operator, name),
                          ('mobile', operator, name)]
            args = expression.OR([args, vat_domain])
            return self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return super(ResPartner, self)._name_search(name, args, operator, limit, name_get_uid)