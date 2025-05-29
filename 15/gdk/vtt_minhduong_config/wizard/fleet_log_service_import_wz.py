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


class FleetLogServicesImportWizard(models.TransientModel):
    _name = 'vtt.fleet.log.services.import.wz'
    _description = 'Fleet Log Services Import Wizard'

    date = fields.Datetime('Date', default=fields.Datetime.now)

    datas = fields.Binary('Datas')
    filename = fields.Char('Filename')

    def submit_log_service_import_wz(self):
        mime = magic.from_buffer(base64.decodebytes(self.datas), mime=True)
        valid_mime = mime in [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
        ]

        service_logs = []

        if valid_mime:
            wb = xlrd.open_workbook(file_contents=base64.decodebytes(self.datas))
            sheet = wb.sheets()[0]

            # DATA KEY
            kw_dict = dict.fromkeys([
                'Biển số xe', 'Loại dịch vụ', 'Mô tả', 'Ngày', 'Chi phí', 'Nhà cung cấp',
                'Ghi chú',
            ], False)
            for col in range(sheet.ncols):
                for k in kw_dict:
                    if sheet.cell(0, col).value.lower().strip() == k.lower().strip():
                        kw_dict[k] = col

            # Check all Valid column
            if all(kw_dict[k] is not False for k in kw_dict) and sheet.nrows > 1:
                # BASE Data
                base_country = self.env.ref('base.vn')
                base_lang = self.env.user.lang

                # Default values
                default_partner_values = {
                    'company_type': 'company',
                    'lang': base_lang,
                    'country_id': base_country.id,
                }
                default_service_values = {
                    'category': 'service'
                }

                # RAW Data
                raw_data_key_map = {
                    'license_plate': 'Biển số xe',
                    'description': 'Mô tả',
                    'service_type_name': 'Loại dịch vụ',
                    'date': 'Ngày',
                    'amount': 'Chi phí',
                    'vendor_name': 'Nhà cung cấp',
                    'notes': 'Ghi chú',
                }

                raw_datas = [
                    {dk: sheet.cell(row, kw_dict[raw_data_key_map[dk]]).value for dk in raw_data_key_map}
                    for row in range(sheet.nrows) if row > 0]

                # SERVICE TYPES
                raw_service_types = {
                    dr['service_type_name']: False for dr in raw_datas if dr['service_type_name']
                }
                for s_type in raw_service_types:
                    s_type_name = s_type.strip()
                    s_type_id = self.env['fleet.service.type'].search([
                        ('name', '=', s_type_name),
                        ('category', '=', 'service')
                    ], limit=1)
                    if not s_type_id:
                        s_type_vals = default_service_values.copy()
                        s_type_vals.update({
                            'name': s_type_name,
                        })
                        s_type_id = self.env['fleet.service.type'].create(s_type_vals)
                    raw_service_types[s_type] = s_type_id

                # VEHICLES
                raw_vehicles = {
                    dr['license_plate']: False for dr in raw_datas if dr['license_plate']
                }
                for lcp in raw_vehicles:
                    vehicle_id = self.env['fleet.vehicle'].search([('license_plate', '=', lcp)], limit=1)
                    if vehicle_id:
                        raw_vehicles[lcp] = vehicle_id

                # VENDORS
                raw_vendors = {
                    dr['vendor_name']: False for dr in raw_datas if dr['vendor_name']
                }
                for vendor in raw_vendors:
                    # vendor_name = vendor.strip()
                    vendor_id = self.env['res.partner'].search([('name', '=', vendor)], limit=1)
                    if not vendor_id:
                        vendor_vals = default_partner_values.copy()
                        vendor_vals.update({
                            'name': vendor,
                        })
                        vendor_id = self.env['res.partner'].create(vendor_vals)
                    raw_vendors[vendor] = vendor_id

                # Loop Service Log Data
                for r_data in raw_datas:
                    if raw_vehicles.get(r_data['license_plate'], False) and raw_service_types.get(r_data['service_type_name'], False):
                        r_log_vals = {
                            'description': r_data['description'],
                            'amount': r_data['amount'],
                            'notes': r_data['notes'],
                            'service_type_id': raw_service_types[r_data['service_type_name']].id,
                            'vehicle_id': raw_vehicles[r_data['license_plate']].id,
                        }
                        if r_data['vendor_name']:
                            r_log_vals['vendor_id'] = raw_vendors[r_data['vendor_name']].id
                        if r_data['date']:
                            if type(r_data['date']) == str:
                                r_date = datetime.strptime(r_data['date'], '%d/%m/%Y')
                            elif type(r_data['date']) in [int, float]:
                                r_date = from_excel_ordinal(r_data['date'])
                            else:
                                r_date = False
                            r_log_vals['date'] = r_date
                        log_id = self.env['fleet.vehicle.log.services'].create(r_log_vals)
                        service_logs.append(log_id.id)

            # RETURN ACTION
                if not service_logs:
                    return {'type': 'ir.actions.act_window_close'}
                else:
                    action = self.env["ir.actions.actions"]._for_xml_id("fleet.fleet_vehicle_log_services_action")
                    if len(service_logs) == 1:
                        form_view = [(self.env.ref('fleet.fleet_vehicle_log_services_view_form').id, 'form')]
                        if 'views' in action:
                            action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
                        else:
                            action['views'] = form_view
                        action['res_id'] = service_logs[0]
                    else:
                        action['domain'] = [('id', 'in', service_logs)]
                return action
            else:
                raise ValidationError(_('Some problem occur from your data details.'
                                        'Please checkout of it.'))
        else:
            raise ValidationError(_('Your file might not valid or included some mistake.'
                                    'Please checkout of it.'))