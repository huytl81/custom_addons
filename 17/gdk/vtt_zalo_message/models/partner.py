from odoo import api, fields, models

import csv
from odoo.tools import file_open

class ResPartner(models.Model):
    _inherit = "res.partner"

    

    def add_zalo_tag(self):
        ab = self
        abc = 'a'

        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Zalo Tag',
            'res_model': 'partner.add.zalo.tag.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_tags_string': 'b',
                'default_shipping_price': 0,
                'default_partner_ids': self.ids,
                'active_ids': self.ids,
                'active_model': self._name,
            },
        }