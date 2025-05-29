# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import magic
import base64
import xlrd
from odoo.exceptions import ValidationError


class PartnerUpdateWizard(models.TransientModel):
    _name = 'vtt.partner.update.wz'
    _description = 'Partner Update Wizard'

    date = fields.Datetime('Date', default=fields.Datetime.now)

    datas = fields.Binary('Datas')
    filename = fields.Char('Filename')

    def submit_partner_update_wz(self):
        mime = magic.from_buffer(base64.decodebytes(self.datas), mime=True)
        valid_mime = mime in [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
        ]

        partners = []

        if valid_mime:
            wb = xlrd.open_workbook(file_contents=base64.decodebytes(self.datas))
            sheet = wb.sheets()[0]

            # DATA KEY
            kw_dict = dict.fromkeys([
                'Mã', 'Tên Liên hệ', 'Địa chỉ', 'Mã số thuế', 'Điện thoại', 'Di động',
                'Email', 'Mã công ty cha', 'Là cá nhân', 'Phân loại',
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

                # RAW Data
                raw_data_key_map = {
                    'vtt_partner_code': 'Mã',
                    'name': 'Tên Liên hệ',
                    'street': 'Địa chỉ',
                    'vat': 'Mã số thuế',
                    'phone': 'Điện thoại',
                    'mobile': 'Di động',
                    'email': 'Email',
                    'parent_code': 'Mã công ty cha',
                    'is_person': 'Là cá nhân',
                    'tag_name': 'Phân loại',
                }

                raw_datas = [
                    {dk: sheet.cell(row, kw_dict[raw_data_key_map[dk]]).value for dk in raw_data_key_map}
                    for row in range(sheet.nrows) if row > 0]

                # TAG
                lst_tag = []
                for rd in raw_datas:
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
                    tag_id = self.env['res.partner.category'].search([('name', '=', tag_name)], limit=1)
                    if not tag_id:
                        tag_id = self.env['res.partner.category'].create({
                            'name': tag_name,
                        })
                    raw_tags[tag] = tag_id

                # PARENTLESS
                lst_parentless_datas = [rd for rd in raw_datas if not rd['parent_code']]
                if lst_parentless_datas:
                    for rd in lst_parentless_datas:
                        p_code = rd['vtt_partner_code'].strip()
                        p_vals = default_partner_values.copy()
                        p_vals.update({
                            'name': rd['name'],
                            'vtt_partner_code': p_code,
                            'street': rd['street'],
                            'vat': rd['vat'],
                            'phone': rd['phone'],
                            'mobile': rd['mobile'],
                            'email': rd['email'],
                            'parent_id': False,
                        })
                        if rd['is_person'] and rd['is_person'] in [1, True]:
                            p_vals['company_type'] = 'person'
                        if rd['tag_name']:
                            lst_p_tag = rd['tag_name'].split(',')
                            p_vals['category_id'] = [(6, 0, [raw_tags[t].id for t in lst_p_tag if t])]
                        partner_id = self.env['res.partner'].search([('vtt_partner_code', '=', p_code)], limit=1)
                        if partner_id:
                            partner_id.write(p_vals)
                        else:
                            partner_id = self.env['res.partner'].create(p_vals)
                        partners.append(partner_id.id)

                # CHILDS
                lst_child_datas = [rd for rd in raw_datas if rd['parent_code']]
                if lst_child_datas:
                    for rd in lst_child_datas:
                        p_code = rd['vtt_partner_code'].strip()
                        p_vals = default_partner_values.copy()
                        p_vals.update({
                            'name': rd['name'],
                            'vtt_partner_code': p_code,
                            'street': rd['street'],
                            'vat': rd['vat'],
                            'phone': rd['phone'],
                            'mobile': rd['mobile'],
                            'email': rd['email'],
                        })
                        p_parent_code = rd['parent_code'].strip()
                        rd_parent = self.env['res.partner'].search([('vtt_partner_code', '=', p_parent_code)], limit=1)
                        p_vals['parent_id'] = rd_parent and rd_parent.id or False
                        if rd['is_person'] and rd['is_person'] in [1, True]:
                            p_vals['company_type'] = 'person'
                        if rd['tag_name']:
                            lst_p_tag = rd['tag_name'].split(',')
                            p_vals['category_id'] = [(6, 0, [raw_tags[t].id for t in lst_p_tag if t])]
                        partner_id = self.env['res.partner'].search([('vtt_partner_code', '=', p_code)], limit=1)
                        if partner_id:
                            partner_id.write(p_vals)
                        else:
                            partner_id = self.env['res.partner'].create(p_vals)
                        partners.append(partner_id.id)

            # RETURN ACTION
                if not partners:
                    return {'type': 'ir.actions.act_window_close'}
                else:
                    action = self.env["ir.actions.actions"]._for_xml_id("contacts.action_contacts")
                    if len(partners) == 1:
                        form_view = [(self.env.ref('base.view_partner_form').id, 'form')]
                        if 'views' in action:
                            action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
                        else:
                            action['views'] = form_view
                        action['res_id'] = partners[0]
                    else:
                        action['domain'] = [('id', 'in', partners)]
                return action
            else:
                raise ValidationError(_('Some problem occur from your partner details.'
                                        'Please checkout of it.'))
        else:
            raise ValidationError(_('Your file might not valid or included some mistake.'
                                    'Please checkout of it.'))