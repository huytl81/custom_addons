# -*- coding: utf-8 -*-
import requests

from odoo import api, fields, models

class PartnerAddZaloTagWizard(models.TransientModel):
    _name = 'partner.add.zalo.tag.wizard'
    _description = 'Partner add Zalo Tag Wizard'

    shipping_price = fields.Float(string='Shipping Price')
    partner_ids = fields.Many2many('res.partner', string='Partners')

    tag_id = fields.Many2one('vtt.zalo.oa.tag', string='Tag')    
        
            # return response.json().get('data', [])

    def confirm(self):
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            partners = self.env['res.partner'].browse(active_ids)

            
            for partner in partners:
                if not partner.zalo_id_by_oa:
                    continue
                self._tag_follower(partner.zalo_id_by_oa, self.tag_id.name)


    def _tag_follower(self, user_id, tag):
        access_token = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_oa_api_access_token')
        url = 'https://openapi.zalo.me/v2.0/oa/tag/tagfollower'
        headers = {'access_token': access_token}
        data = {'user_id': user_id, 'tag_name': tag}
        response = requests.post(url, headers=headers, json=data)
        return response.status_code == 200