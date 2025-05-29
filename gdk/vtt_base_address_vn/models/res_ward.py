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
    # ghn_ward_id = fields.Char("GHN Ward Code")

    code = fields.Char('Mã phường xã')

    @api.model
    def _load_data(self):
        ab = ''
        with file_open('vtt_base_address_vn/data/default_data.csv', 'r') as csv_file:
            # load all
            # trong for sẽ nhóm ra state, district, ward
            # tiếp theo sẽ thêm vào

            datas = []
            f_key = ''

            current_state = None
            current_district = None

            country = self.env['res.country'].sudo().search([['code', '=', 'VN']], limit=1)
            count = 1
            try:

                for row in csv.DictReader(csv_file):
                    count = count + 1

                    datas.append({key: value for key, value in row.items()})
                    if f_key == '': f_key = next(iter(datas[0]))
                    state_code = row[f_key]
                    dis_code = row['huyen_code']
                    ward_code = row['xa_code']
                    state_name = row['tinh']
                    dis_name = row['huyen']
                    war_name = row['xa']

                    # load first, run 1 time
                    if not current_state:
                        current_state = self.env['res.country.state'].sudo().search([['name', '=', state_name]],
                                                                                    limit=1)
                        if not current_state:
                            current_state = self.env['res.country.state'].sudo().create({
                                'name': state_name, 'state_code': state_code, 'country_id': country.id,
                                'code': 'BB' + str(count)
                            })

                    if current_state:
                        # neu state name thay doi -> load lai
                        if current_state.name != state_name:
                            current_state = self.env['res.country.state'].sudo().search([['name', '=', state_name]],
                                                                                        limit=1)
                            if not current_state:
                                current_state = self.env['res.country.state'].sudo().create({
                                    'name': state_name, 'state_code': state_code, 'country_id': country.id,
                                    'code': 'BB' + str(count)
                                })
                        # update state code neu chua co
                        if not current_state.state_code or current_state.code == '':
                            current_state.write({'state_code': state_code})

                        # load first district
                        if not current_district:
                            current_district = self.env['res.district'].sudo().search([['name', '=ilike', dis_name]],
                                                                                      limit=1)
                            if not current_district:
                                current_district = self.env['res.district'].sudo().create({
                                    'name': dis_name, 'code': dis_code, 'country_id': country.id,
                                    'state_id': current_state.id
                                })

                        if current_district:
                            # neu district name thay doi -> load lai
                            if current_district.name != dis_name:
                                current_district = self.env['res.district'].sudo().search(
                                    [['name', '=ilike', dis_name]], limit=1)
                                if not current_district:
                                    current_district = self.env['res.district'].sudo().create({
                                        'name': dis_name, 'code': dis_code, 'country_id': country.id,
                                        'state_id': current_state.id
                                    })
                            # update district code neu chua co
                            if not current_district.code or current_district.code == '':
                                current_district.write({'code': dis_code})

                            # them ward
                            self.env['res.ward'].sudo().create({
                                'name': war_name, 'code': ward_code, 'country_id': country.id,
                                'state_id': current_state.id, 'district_id': current_district.id
                            })

                    # current_district = self.env['res.district'].sudo().search([['name', '=', dis_name]], limit=1)
                    bb = ''
            except Exception as e:
                raise ValueError(f"Error loading ward data: {e}")
