from odoo import api, fields, models, _
import requests
import csv
from odoo.tools import file_open


class ResWard(models.Model):
    _name = 'res.ward'
    _description = 'Res Ward'
    _order = 'state_id'

    name = fields.Char("Name", required=True, translate=True)
    country_id = fields.Many2one('res.country', string='Country', required=True)
    state_id = fields.Many2one('res.country.state', 'State', domain="[('country_id', '=', country_id)]")
    district_id = fields.Many2one('res.district', 'District', domain="[('state_id', '=', state_id)]")
    ghn_ward_id = fields.Char("GHN Ward Code")

    @api.model
    def _load_ward_data(self):
        with file_open('vtt_ghn_integration/data/default_res_ward.csv', 'r') as csv_file:
            datas = []
            for row in csv.DictReader(csv_file):
                datas.append({key: value for key, value in row.items()})

            all_ward = set(self.search([]).mapped('ghn_ward_id'))
            datas_valid = [r for r in datas if r['ghn_ward_id'] not in all_ward]
            lst_district = set([r['district_id'] for r in datas_valid])

            district_datas = {}
            for pid in lst_district:
                p = self.env['res.district'].search([('ghn_district_id', '=', int(pid))])
                district_datas[pid] = p

            vals = []
            for r in datas_valid:
                if r['district_id'] and r['ghn_ward_id']:
                    if district_datas.get(r['district_id'], False):
                        district = district_datas[r['district_id']]
                        vals.append({
                            'name': r['name'],
                            'state_id': district.state_id.id,
                            'country_id': district.country_id.id,
                            'district_id': district.id,
                            'ghn_ward_id': r['ghn_ward_id'],
                        })

            created_records = self.env['res.ward'].create(vals)
            return created_records

    def create_ward_data(self):
        # request_url = "https://online-gateway.ghn.vn/shiip/public-api/master-data/ward"
        # request_url = "https://dev-online-gateway.ghn.vn/shiip/public-api/master-data/ward?district_id"
        request_url = "https://dev-online-gateway.ghn.vn/shiip/public-api/master-data/ward"
        ghn_token = self.env['ir.config_parameter'].sudo().get_param('ghn_token')
        headers = {
            'Content-type': 'application/json',
            'Token': ghn_token
        }

        # list by district
        ex_districts = self.env['res.district'].sudo().search([('ghn_district_id', '!=', False), ('ghn_district_id', '!=', 0)])
        ex_districts = ex_districts.filtered(lambda d: d.state_id.id == 1073)
        for d in ex_districts:
            district_id = d.ghn_district_id
            params = {'district_id': district_id}
            req = requests.get(request_url, headers=headers, params=params)
            req.raise_for_status()
            content = req.json()
            data = content['data']
            if data:
                data_vals = [{
                    'name': rec['WardName'],
                    'state_id': d.state_id.id,
                    'country_id': d.country_id.id,
                    'district_id': d.id,
                    'ghn_ward_id': rec['WardCode'],
                } for rec in data]
                if data_vals:
                    self.env['res.ward'].sudo().create(data_vals)
            else:
                print(d.name, d.id, d.ghn_district_id)


        # req = requests.get(request_url, headers=headers)
        # req.raise_for_status()
        # content = req.json()
        # data = content['data']
        # for rec in data:
        #     existed_district = self.env['res.district'].sudo().search([('ghn_district_id', '=', rec['DistrictID'])],limit=1)
        #     if existed_district:
        #         vals = {}
        #         vals['state_id'] = existed_district.state_id.id
        #         vals['country_id'] = existed_district.country_id.id
        #         vals['district_id'] = existed_district.id
        #         vals['name'] = rec['WardName']
        #         vals['ghn_ward_id'] = rec['WardCode']
        #         self.env['res.ward'].sudo().create(vals)