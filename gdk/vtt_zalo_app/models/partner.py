
from odoo import api, fields, models

import csv
from odoo.tools import file_open

class ResPartner(models.Model):
    _inherit = "res.partner"



    zalo_id_by_oa = fields.Char(string='Zalo id by OA')             # user id by oa
    zalo_id = fields.Char(string='Zalo id by App')             # user id by app
    zalo_name = fields.Char(string='Zalo name')
    zalo_picture = fields.Char(string='Zalo picture')

    is_default_address = fields.Boolean(default=False, string='Is default address')
    birth_day = fields.Date(string='Birth day')
    sex = fields.Selection([('male', 'Nam'), ('female', 'Nữ')], default='male')

    # follow oa
    followed_oa = fields.Boolean(default=False, string='Followed Zalo OA')      # tương ứng với field user_is_follower của user zalo oa
    followed_oa_time = fields.Datetime(string='Followed OA time')               # Ghi nhận thời điểm follow, mặc định là None
    unfollowed_oa_time = fields.Datetime(string='Unfollowed OA time')           # Ghi nhận thời điểm bỏ follow
    first_time_followed_oa = fields.Datetime(string='Is first time followed OA') # Chỉ ghi nhận lần đầu


    is_deleted = fields.Boolean(default=False)


    def load_ward_data(self):
        ab = ''
        with file_open('vtt_zalo_app/default_res_ward.csv', 'r') as csv_file:
            datas = []
            f_key = ''
            seen_ward = set()
            seen_district = set()

            for row in csv.DictReader(csv_file):
                datas.append({key: value for key, value in row.items()})
                if f_key == '': f_key = next(iter(datas[0]))
                seen_district.add(row['huyen_code'])

            ccc = 'xa'
            ca = datas[0]
            cccc = datas[0][f_key]
            ab = datas[0][ccc]
            cc = ''

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

            a = ''

            # created_records = self.env['res.ward'].create(vals)
            # return created_records





