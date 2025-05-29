# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # birthday = fields.Date('Birthday')

    anniversary_ids = fields.One2many('vtt.contact.anniversary', 'partner_id', 'Events')
    is_incoming_anniversary = fields.Boolean('Incoming Anniversary', compute='_compute_incoming_anniversary')

    def _compute_incoming_anniversary(self):
        date_interval_param = self.env['ir.config_parameter'].sudo().get_param(
            'vtt_contact_anniversary.anniversary_activity_interval', default='0')
        try:
            date_interval = int(date_interval_param)
        except ValueError:
            date_interval = 0
        if date_interval < 0:
            date_interval = 0
        next_date = fields.Date.today() + relativedelta(days=date_interval)
        # ee = self.env['vtt.contact.anniversary'].read_group([
        #     ('next_date', '>=', fields.Date.today()),
        #     ('next_date', '<=', next_date)
        # ], ['id'], ['partner_id'])
        # print(ee)
        events = dict((item['partner_id'][0], item['partner_id_count']) for item in self.env['vtt.contact.anniversary'].read_group([
            ('next_date', '>=', fields.Date.today()),
            ('next_date', '<=', next_date)
        ], ['id'], ['partner_id']))
        for p in self:
            p.is_incoming_anniversary = bool(events.get(p.id, 0))
            # p.is_incoming_anniversary = False

    def view_anniversary(self):
        calendars_action = self.env['ir.actions.act_window']._for_xml_id('vtt_contact_anniversary.vtt_act_window_contact_anniversary_personal_calendar')
        # calendars_action['domain'] = [('partner_ids', 'in', self.id)]
        calendars_action['domain'] = [('partner_id', '=', self.id)]
        # calendars_action['context'] = {
        #     'default_type': 'personal',
        #     'default_partner_ids': [(4, self.id)]
        # }
        calendars_action['context'] = {
            'partner_id': self.id,
            'default_partner_id': self.id,
        }
        return calendars_action

    def make_ann_events(self):
        print('Calteronal')