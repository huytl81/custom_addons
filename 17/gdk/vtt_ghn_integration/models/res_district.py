# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, _
from odoo.tools import file_open
import requests
import csv

_logger = logging.getLogger(__name__)


class ResDistrict(models.Model):
    _name = 'res.district'
    _description = 'District'
    _order = 'state_id'

    name = fields.Char("Name", required=True, translate=True)
    country_id = fields.Many2one('res.country', string='Country', required=True)
    state_id = fields.Many2one(
        'res.country.state', 'State', domain="[('country_id', '=', country_id)]")
    ghn_district_id = fields.Integer('GHN District ID', help='District ID for GHN delivery method')

    @api.model
    def _load_district_data(self):
        with file_open('vtt_ghn_integration/data/default_res_district.csv', 'r') as csv_file:
            datas = []
            for row in csv.DictReader(csv_file):
                datas.append({key: value for key, value in row.items()})

            all_district = set(self.search([]).mapped('ghn_district_id'))
            datas_valid = [r for r in datas if int(r['ghn_district_id']) not in all_district]
            lst_provine = set([r['provine_id'] for r in datas_valid])

            provine_datas = {}
            for pid in lst_provine:
                p = self.env['res.country.state'].search([('ghn_province_id', '=', int(pid))])
                provine_datas[pid] = p

            vals = []
            for r in datas_valid:
                if r['provine_id'] and r['ghn_district_id']:
                    if provine_datas.get(r['provine_id'], False):
                        provine = provine_datas[r['provine_id']]
                        vals.append({
                            'name': r['name'],
                            'state_id': provine.id,
                            'country_id': provine.country_id.id,
                            'ghn_district_id': int(r['ghn_district_id']),
                        })

            created_records = self.env['res.district'].create(vals)
            return created_records

    def create_district_data(self):
        # request_url = "https://online-gateway.ghn.vn/shiip/public-api/master-data/district"
        request_url = "https://dev-online-gateway.ghn.vn/shiip/public-api/master-data/district"
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
            existed_state = self.env['res.country.state'].sudo().search([('ghn_province_id', '=', rec['ProvinceID'])], limit=1)
            if existed_state:
                vals = {}
                vals['state_id'] = existed_state.id
                vals['country_id'] = existed_state.country_id.id
                vals['name'] = rec['DistrictName']
                vals['ghn_district_id'] = rec['DistrictID']
                self.env['res.district'].sudo().create(vals)
