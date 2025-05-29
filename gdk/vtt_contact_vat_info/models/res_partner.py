# -*- coding: utf-8 -*-

import json
from odoo import models, fields, api, _
import requests
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _contact_address_parser(self, address):

        def _get_country(country_name):
            return self.env['res.country'].search([('name', 'ilike', country_name)])

        def _get_country_state(country_state_name, country_id=False):
            domain = [('name', 'ilike', country_state_name)]
            if country_id:
                domain.append(('country_id', '=', country_id.id))
            return self.env['res.country.state'].search(domain)

        def _get_country_state_name(country_state_name):
            lst_province_prefix = ['tỉnh', 'tp', 'thành phố', 'tp.']
            name = country_state_name.lower()
            for e in lst_province_prefix:
                name = name.replace(e, '')
            return name.strip()

        if address:
            lst_address = address.split(', ')
            country = _get_country(lst_address[-1])
            if country:
                province_name = _get_country_state_name(lst_address[-2])
                province = _get_country_state(province_name, country)
                if province:
                    street = ', '.join(lst_address[:-2])
                else:
                    street = ', '.join(lst_address[:-1])
            else:
                province_name = _get_country_state_name(lst_address[-1])
                province = _get_country_state(province_name)
                if province:
                    street = ', '.join(lst_address[:-1])
                else:
                    street = address

            return street, province, country

        else:
            return '', False, False

    def _get_contact_info_by_vat(self, vat):
        base_url = 'https://api.vietqr.io/v2/business/'
        vat_url = base_url + vat
        response = requests.get(vat_url)
        if response.status_code == 200:
            result = {'success': True, 'content': response.json()}
        else:
            result = {'success': False}
        return result

    def get_contact_info_external(self):
        self.ensure_one()
        if self.vat:
            contact_data = self._get_contact_info_by_vat(self.vat)
            if contact_data['success']:
                if contact_data['content'].get('code') == '00':
                    contact_content = contact_data['content']['data']
                    name = contact_content['name']
                    international_name = contact_content['internationalName']
                    address = contact_content['address']
                    street, country_state, country = self._contact_address_parser(address)

                    self.name = name
                    self.street = street
                    self.state_id = country_state.id
                    self.country_id = country.id
                else:
                    raise UserError(_('The VAT number is not valid.'))
            else:
                raise UserError(_('The VAT number service is not connected. Please report to your Admin for more information'))