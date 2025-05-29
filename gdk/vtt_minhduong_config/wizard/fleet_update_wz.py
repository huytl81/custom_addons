# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import magic
import base64
import xlrd
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


def from_excel_ordinal(ordinal: float, _epoch0=datetime(1899, 12, 31)) -> datetime:
    if ordinal >= 60:
        ordinal -= 1  # Excel leap year bug, 1900 is not a leap year!
    return (_epoch0 + timedelta(days=ordinal)).replace(microsecond=0)


class FleetUpdateWizard(models.TransientModel):
    _name = 'vtt.fleet.update.wz'
    _description = 'Fleet Update Wizard'

    date = fields.Datetime('Date', default=fields.Datetime.now)

    datas = fields.Binary('Datas')
    filename = fields.Char('Filename')

    def submit_fleet_update_wz(self):
        mime = magic.from_buffer(base64.decodebytes(self.datas), mime=True)
        valid_mime = mime in [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
        ]

        vehicle_models = []
        vehicles = []

        if valid_mime:
            wb = xlrd.open_workbook(file_contents=base64.decodebytes(self.datas))
            model_sheet = wb.sheet_by_name('Model Sheet')
            vehicle_sheet = wb.sheet_by_name('Vehicle Sheet')

            # DATA KEY
            model_kw_dict = dict.fromkeys([
                'Nhà sản xuất', 'Dòng xe', 'Năm sản xuất', 'Loại phương tiện', 'Hộp số', 'Số ghế',
                'Số cửa', 'Công suất', 'Loại nhiên liệu', 'Màu sắc',
            ], False)
            for col in range(model_sheet.ncols):
                for k in model_kw_dict:
                    if model_sheet.cell(0, col).value.lower().strip() == k.lower().strip():
                        model_kw_dict[k] = col
            vehicle_kw_dict = dict.fromkeys([
                'Biển số xe', 'Nhà sản xuất', 'Dòng xe', 'Tài xế', 'Điện thoại', 'Ngày đăng kiểm',
                'Số khung', 'Công tơ mét', 'Thẻ',
            ], False)
            for col in range(vehicle_sheet.ncols):
                for k in vehicle_kw_dict:
                    if vehicle_sheet.cell(0, col).value.lower().strip() == k.lower().strip():
                        vehicle_kw_dict[k] = col

            # VEHICLE MODEL
            # Check all Valid column
            if all(model_kw_dict[k] is not False for k in model_kw_dict) and model_sheet.nrows > 1:
                # BASE Data
                # base_country = self.env.ref('base.vn')
                # base_lang = self.env.user.lang

                # Selection dict
                select_vehicle_type = {
                    'Ô tô': 'car',
                    'Xe máy': 'motorbike',
                    'Xe đạp': 'bike',
                }
                select_transmission = {
                    'Thủ công': 'manual',
                    'Tự động': 'automatic',
                }
                select_default_fuel_type = {
                    'Dầu Diesel': 'diesel',
                    'Xăng': 'gasoline',
                    'Hybrid Diesel': 'hybrid',
                    'Hybrid Gasoline': 'full_hybrid_gasoline',
                    'Plug-in Hybrid Diesel': 'plug_in_hybrid_diesel',
                    'Plug-in Hybrid Gasoline': 'plug_in_hybrid_gasoline',
                    'CNG': 'cng',
                    'LPG': 'lpg',
                    'Hydrogen': 'hydrogen',
                    'Điện': 'electric',
                }

                # Default values
                default_model_values = {
                    'vehicle_type': 'car',
                    'default_fuel_type': 'diesel',
                }

                # RAW Data
                raw_data_model_key_map = {
                    'name': 'Dòng xe',
                    'brand_name': 'Nhà sản xuất',
                    'model_year': 'Năm sản xuất',
                    'vehicle_type_name': 'Loại phương tiện',
                    'transmission_name': 'Hộp số',
                    'seats': 'Số ghế',
                    'doors': 'Số cửa',
                    'color': 'Màu sắc',
                    'default_fuel_type_name': 'Loại nhiên liệu',
                    'power': 'Công suất',
                }

                raw_model_datas = [
                    {dk: model_sheet.cell(row, model_kw_dict[raw_data_model_key_map[dk]]).value for dk in raw_data_model_key_map}
                    for row in range(model_sheet.nrows) if row > 0]

                # BRAND
                raw_brands = {
                    dr['brand_name']: False for dr in raw_model_datas if dr['brand_name']
                }
                for brand in raw_brands:
                    brand_name = brand.strip()
                    brand_id = self.env['fleet.vehicle.model.brand'].search([('name', '=', brand_name)], limit=1)
                    if not brand_id:
                        brand_id = self.env['fleet.vehicle.model.brand'].create({
                            'name': brand_name,
                        })
                    raw_brands[brand] = brand_id

                # Loop Model Data
                for r_data in raw_model_datas:
                    if r_data['brand_name']:
                        r_brand_id = raw_brands[r_data['brand_name']]
                        model_name = r_data['name'].strip()
                        r_vals = {
                            'brand_id': r_brand_id and r_brand_id.id or False,
                            'name': model_name,
                            'model_year': r_data['model_year'],
                            'seats': r_data['seats'],
                            'doors': r_data['doors'],
                            'color': r_data['color'],
                            'power': r_data['power'],
                        }
                        if r_data['vehicle_type_name'] and select_vehicle_type.get(r_data['vehicle_type_name'].strip()):
                            r_vals['vehicle_type'] = select_vehicle_type[r_data['vehicle_type_name'].strip()]
                        if r_data['transmission_name'] and select_transmission.get(r_data['transmission_name'].strip()):
                            r_vals['transmission'] = select_transmission[r_data['transmission_name'].strip()]
                        if r_data['default_fuel_type_name'] and select_default_fuel_type.get(r_data['default_fuel_type_name'].strip()):
                            r_vals['default_fuel_type'] = select_default_fuel_type[r_data['default_fuel_type_name'].strip()]
                        model_id = self.env['fleet.vehicle.model'].search([
                            ('brand_id', '=', r_brand_id.id),
                            ('name', '=', model_name)
                        ], limit=1)
                        if model_id:
                            model_id.write(r_vals)
                        else:
                            model_id = self.env['fleet.vehicle.model'].create(r_vals)
                        vehicle_models.append(model_id.id)

            # VEHICLE
            # Check all Valid column
            if all(vehicle_kw_dict[k] is not False for k in vehicle_kw_dict) and vehicle_sheet.nrows > 1:
                # BASE Data
                base_country = self.env.ref('base.vn')
                base_lang = self.env.user.lang

                # Default values
                default_driver_values = {
                    'company_type': 'person',
                    'lang': base_lang,
                    'country_id': base_country.id,
                }

                # RAW Data
                raw_data_vehicle_key_map = {
                    'license_plate': 'Biển số xe',
                    'brand_name': 'Nhà sản xuất',
                    'model_name': 'Dòng xe',
                    'driver_name': 'Tài xế',
                    'driver_mobile': 'Điện thoại',
                    'acquisition_date': 'Ngày đăng kiểm',
                    'vin_sn': 'Số khung',
                    'odometer': 'Công tơ mét',
                    'tag_name': 'Thẻ',
                }

                raw_vehicle_datas = [
                    {dk: vehicle_sheet.cell(row, vehicle_kw_dict[raw_data_vehicle_key_map[dk]]).value for dk in
                     raw_data_vehicle_key_map}
                    for row in range(vehicle_sheet.nrows) if row > 0]

                # TAG
                lst_tag = []
                for rd in raw_vehicle_datas:
                    if rd['tag_name']:
                        rd_tags = rd['tag_name'].split(',')
                        for t in rd_tags:
                            if t.strip() and t.strip() not in lst_tag:
                                lst_tag.append(t)
                raw_tags = {
                    t: False for t in lst_tag
                }
                for tag in raw_tags:
                    tag_name = tag.strip()
                    tag_id = self.env['fleet.vehicle.tag'].search([('name', '=', tag_name)], limit=1)
                    if not tag_id:
                        tag_id = self.env['fleet.vehicle.tag'].create({
                            'name': tag_name,
                        })
                    raw_tags[tag] = tag_id

                # DRIVER
                raw_drivers = {
                    dr['driver_name']: {
                        'name': dr['driver_name'].strip(),
                        'mobile': dr['driver_mobile'],
                    } for dr in raw_vehicle_datas if dr['driver_name']
                }
                for driver in raw_drivers:
                    driver_name = driver.strip()
                    driver_id = self.env['res.partner'].search([('name', '=', driver_name)], limit=1)
                    if not driver_id:
                        driver_vals = default_driver_values.copy()
                        driver_vals.update({'name': driver_name, 'mobile': raw_drivers[driver]['mobile']})
                        driver_id = self.env['res.partner'].create(driver_vals)
                    else:
                        driver_id.write({'mobile': raw_drivers[driver]['mobile']})
                    raw_drivers[driver]['driver_id'] = driver_id

                # Loop Vehicle Data
                for r_data in raw_vehicle_datas:
                    lcp = r_data['license_plate']
                    vehicle_vals = {
                        # 'acquisition_date': r_data['acquisition_date'],
                        'vin_sn': r_data['vin_sn'],
                        'odometer': r_data['odometer'],
                    }
                    if r_data['acquisition_date']:
                        # r_acquisition_date = datetime(*xlrd.xldate_as_tuple(r_data['acquisition_date'], wb.datemode))
                        if type(r_data['acquisition_date']) == str:
                            r_acquisition_date = datetime.strptime(r_data['acquisition_date'], '%d/%m/%Y')
                        elif type(r_data['acquisition_date']) in [int, float]:
                            r_acquisition_date = from_excel_ordinal(r_data['acquisition_date'])
                        else:
                            r_acquisition_date = False
                        vehicle_vals['acquisition_date'] = r_acquisition_date
                    if r_data['driver_name']:
                        vehicle_vals['driver_id'] = raw_drivers[r_data['driver_name']]['driver_id'].id
                    if r_data['tag_name']:
                        lst_v_tag = r_data['tag_name'].split(',')
                        vehicle_vals['tag_ids'] = [(6, 0, [raw_tags[t].id for t in lst_v_tag if t])]
                    vehicle_id = self.env['fleet.vehicle'].search([('license_plate', '=', lcp)], limit=1)
                    if vehicle_id:
                        vehicle_id.write(vehicle_vals)
                        vehicle_id._compute_model_fields()
                        vehicles.append(vehicle_id.id)
                    else:
                        brand_name = r_data['brand_name'].strip()
                        brand_id = self.env['fleet.vehicle.model.brand'].search([('name', '=', brand_name)], limit=1)
                        if brand_id:
                            model_name = r_data['model_name'].strip()
                            model_id = self.env['fleet.vehicle.model'].search([
                                ('brand_id', '=', brand_id.id),
                                ('name', '=', model_name)
                            ], limit=1)
                            if model_id:
                                vehicle_vals.update({
                                    'license_plate': lcp,
                                    'model_id': model_id.id,
                                })
                                vehicle_id = self.env['fleet.vehicle'].create(vehicle_vals)
                                vehicle_id._compute_model_fields()
                                vehicles.append(vehicle_id.id)

            if vehicles or vehicle_models:
                return {'type': 'ir.actions.act_window_close'}
            else:
                raise ValidationError(_('Some problem occur from your data details.'
                                        'Please checkout of it.'))
        else:
            raise ValidationError(_('Your file might not valid or included some mistake.'
                                    'Please checkout of it.'))