# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def get_py3o_report_data(self):
        self.ensure_one()
        return {
            'name': self.name or '',
            'parent_name': self.parent_id and self.parent_id.name or '',
            'phone': self.phone or '',
            'email': self.email or '',
            'mobile': self.mobile or '',
            'website': self.website or '',
            # 'parent_id': self.parent_id and self.parent_id.get_py3o_report_data() or {},
            'street': self.street or '',
            'street2': self.street2 or '',
            'city': self.city or '',
            'state_id': self.state_id and self.state_id.name or '',
            'country_id': self.country_id and self.country_id.name or '',
        }
