# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv import expression
from . import analysis_tools


class InvestigateLocation(models.Model):
    _name = 'investigate.location'
    _description = 'Investigate Location'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'threat.sync.mixin']
    _order = 'name'

    name = fields.Char('Name')
    address_id = fields.Many2one('res.partner', 'Address Contact')

    def _get_default_country(self):
        return self.env.company.partner_id.country_id

    street = fields.Char('Street')
    ward = fields.Char('Ward')
    district = fields.Char('City/ District')
    country_id = fields.Many2one('res.country', string='Country', required=True, default=_get_default_country)
    country_code = fields.Char(related='country_id.code')
    state_id = fields.Many2one('res.country.state', string='State')

    full_address = fields.Char('Full Address', compute='_compute_full_address', store=True)

    # Geo location
    partner_latitude = fields.Float(string='Geo Latitude', digits=(16, 5))
    partner_longitude = fields.Float(string='Geo Longitude', digits=(16, 5))

    phone = fields.Char('Phone')
    email = fields.Char('Email')

    # Investigate History
    campaign_ids = fields.One2many('investigate.campaign', 'location_id', 'Campaigns')

    campaign_count = fields.Integer('Campaign Count', compute='_compute_campaign_count')

    ss_code = fields.Char('Secret Sequence', copy=False)

    def _compute_campaign_count(self):
        for location in self:
            location.campaign_count = len(location.campaign_ids)

    @api.depends('street', 'ward', 'district', 'state_id', 'country_id')
    def _compute_full_address(self):
        for loc in self:
            full_address = f'{loc.country_id.name}'
            if loc.state_id:
                full_address = f'{loc.state_id.name}, ' + full_address
            if loc.district:
                full_address = f'{loc.district}, ' + full_address
            if loc.ward:
                full_address = f'{loc.ward}, ' + full_address
            if loc.street:
                full_address = f'{loc.street}, ' + full_address
            loc.full_address = full_address

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('name', operator, name), ('full_address', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    @api.model
    def create(self, vals):
        location = super(InvestigateLocation, self).create(vals)
        partner_vals = {
            'name': location.name,
            'street': location.street,
            'street2': location.ward,
            'city': location.district,
            'state_id': location.state_id.id,
            'country_id': location.country_id.id,
            'company_type': 'company',
            'lang': self.env.lang,
            'email': location.email,
            'phone': location.phone,
        }
        if 'partner_latitude' in vals:
            partner_vals.update({
                'partner_latitude': vals['partner_latitude']
            })
        if 'partner_longitude' in vals:
            partner_vals.update({
                'partner_longitude': vals['partner_longitude']
            })
        partner = self.env['res.partner'].create(partner_vals)
        location.address_id = partner
        if 'partner_longitude' not in vals:
            location.partner_longitude = partner.partner_longitude
        if 'partner_latitude' not in vals:
            location.partner_latitude = partner.partner_latitude
        return location

    def write(self, vals):
        contact_field_mapper = [
            ('name', 'name'),
            ('street', 'street'),
            ('ward', 'street2'),
            ('district', 'city'),
            ('state_id', 'state_id'),
            ('country_id', 'country_id'),
            ('partner_latitude', 'partner_latitude'),
            ('partner_longitude', 'partner_longitude'),
            ('phone', 'phone'),
            ('email', 'email')
        ]
        fields_check = [f[0] for f in contact_field_mapper]
        if any(f in vals for f in fields_check):
            changes = [m for m in contact_field_mapper if m[0] in vals]
            partner = self.address_id

            partner_vals = {m[1]:vals[m[0]] for m in changes}
            partner.write(partner_vals)
            if 'partner_latitude' not in vals and 'partner_longitude' not in vals:
                vals.update({
                    'partner_latitude': partner.partner_latitude,
                    'partner_longitude': partner.partner_longitude
                })
        res = super(InvestigateLocation, self).write(vals)
        return res
