# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import requests


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    ghn_province_id = fields.Integer(string="GHN State ID", help='State ID for GHN delivery method')

    def fetch_all_province_id(self):
        # request_url = "https://online-gateway.ghn.vn/shiip/public-api/master-data/province"
        request_url = "https://dev-online-gateway.ghn.vn/shiip/public-api/master-data/province"
        ghn_token = self.env['ir.config_parameter'].sudo().get_param('ghn_token')
        headers = {
            'Content-type': 'application/json',
            'Token': ghn_token
        }
        req = requests.get(request_url, headers=headers)
        req.raise_for_status()
        content = req.json()
        data = content['data']
        for rec in data:
            existed_state = self.env['res.country.state'].sudo().search([('name', 'ilike', rec['ProvinceName'])])
            if existed_state:
                for e in existed_state:
                    e.sudo().write({
                        'ghn_province_id': rec['ProvinceID']
                    })
        return content


