# -*- coding: utf-8 -*-
import requests

from odoo import api, fields, models

class QuickCreatePartner(models.TransientModel):
    _name = 'quick.create.partner'
    _description = 'Quick Create Partner'

    # name
    # phone
    # street
    # ward_id

    # delivery_name
    # delivery_phone
    # delivery_street
    # delivery_ward_id

    name = fields.Char(string='Tên', required=True)
    phone = fields.Char(string='Số điện thoại')
    street = fields.Char(string='Địa chỉ')
    ward_id = fields.Many2one('res.ward', string='Phường/Xã, Quận/Huyện, Tỉnh/TP')
    full_text_address = fields.Char(string='Địa chỉ đầy đủ')

    delivery_name = fields.Char(string='Người nhận')
    delivery_phone = fields.Char(string='Số điện thoại')
    delivery_street = fields.Char(string='Địa chỉ')
    delivery_ward_id = fields.Many2one('res.ward', string='Phường/Xã, Quận/Huyện, Tỉnh/TP')
    full_text_delivery_address = fields.Char(string='Địa chỉ đầy đủ')

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            self.delivery_name = self.name

    @api.onchange('phone')
    def _onchange_phone(self):
        if self.phone:
            self.delivery_phone = self.phone

    @api.onchange('street')
    def _onchange_street(self):
        if self.street:
            self.delivery_street = self.street
            self.full_text_address = f"{self.street}, {self.ward_id.name}, {self.ward_id.district_id.name}, {self.ward_id.district_id.state_id.name}"            

    @api.onchange('ward_id')
    def _onchange_ward_id(self):
        if self.ward_id:
            self.full_text_address = f"{self.street}, {self.ward_id.name}, {self.ward_id.district_id.name}, {self.ward_id.district_id.state_id.name}"
            self.delivery_ward_id = self.ward_id

    @api.onchange('delivery_street')
    def _onchange_delivery_street(self):
        if self.delivery_street:
            self.full_text_delivery_address = f"{self.delivery_street}, {self.delivery_ward_id.name}, {self.delivery_ward_id.district_id.name}, {self.delivery_ward_id.district_id.state_id.name}"

    @api.onchange('delivery_ward_id')
    def _onchange_delivery_ward_id(self):
        if self.delivery_ward_id:
            self.full_text_delivery_address = f"{self.delivery_street}, {self.delivery_ward_id.name}, {self.delivery_ward_id.district_id.name}, {self.delivery_ward_id.district_id.state_id.name}"

    def copy(self):
        self.delivery_name = self.name
        self.delivery_phone = self.phone
        self.delivery_street = self.street
        self.delivery_ward_id = self.ward_id

    def confirm(self):
        # check phone da ton tai chua
        # count = self.env['res.partner'].search_count([
        #     ('type', '=', 'contact'),
        #     '|',
        #     ('phone', '=', self.phone),
        #     ('mobile', '=', self.phone)
        # ])

        # if count > 0:
        vals = {
            'name': self.name,
            'phone': self.phone,
            'street': self.street,
            'type': 'contact',
            'is_zalo_customer': True,
        }
        if self.ward_id:
            vals['ward_id'] = self.ward_id.id
            vals['district_id'] = self.ward_id.district_id.id
            vals['state_id'] = self.ward_id.district_id.state_id.id
            vals['country_id'] = self.ward_id.district_id.state_id.country_id.id
            
        partner = self.env['res.partner'].create(vals)
        if partner and self.delivery_name:
            d_vals = {
                'name': self.delivery_name,
                'phone': self.delivery_phone,
                'street': self.delivery_street,
                'type': 'delivery',
                'parent_id': partner.id,
                'is_default_address': True,
            }
            if self.delivery_ward_id:
                d_vals['ward_id'] = self.delivery_ward_id.id
                d_vals['district_id'] = self.delivery_ward_id.district_id.id
                d_vals['state_id'] = self.delivery_ward_id.district_id.state_id.id
                d_vals['country_id'] = self.delivery_ward_id.district_id.state_id.country_id.id

            delivery_partner = self.env['res.partner'].create(d_vals)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'res_id': partner.id,
            'view_mode': 'form',
            'target': 'current',
        }