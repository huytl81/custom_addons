# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class VttContactAnniversary(models.Model):
    _name = 'vtt.contact.anniversary'
    _description = 'Contact Anniversary'
    _order = 'next_date, name'

    name = fields.Char('Name', required=True)
    int_day = fields.Integer('Day', compute='_compute_day_month', store=True)
    int_month = fields.Integer('Month', compute='_compute_day_month', store=True)
    description = fields.Text('Description')
    count = fields.Integer('Count')
    date = fields.Date('Date', required=True)
    next_date = fields.Date('Next Date')

    partner_id = fields.Many2one('res.partner', 'Partner', required=True)

    interval_number = fields.Integer('Recurrent', default=1)
    interval_type = fields.Selection([
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
        ('year', 'Year')
    ], 'Recurrent Type', required=True, default='year')

    active = fields.Boolean('Active', default=True)
    is_planned = fields.Boolean('Planned', default=False)

    category_id = fields.Many2one('vtt.contact.anniversary.category', 'Category')

    @api.onchange('category_id')
    def onchange_category_id(self):
        if self.category_id:
            if not self.name:
                self.name = self.category_id.name
            self.interval_type = self.category_id.interval_type
            self.interval_number = self.category_id.interval_number

    def _cron_next_date(self):
        events = self.search([
            ('next_date', '<=', fields.Date.today())
        ])
        if events:
            for e in events:
                e.next_date = e._get_next_date(e.next_date, e.interval_number, e.interval_type)
                e.is_planned = False
        return True

    @api.depends('date')
    def _compute_day_month(self):
        for t in self:
            if t.date:
                t.int_month = t.date.month
                t.int_day = t.date.day

    @api.model
    def create(self, vals):
        res = super(VttContactAnniversary, self).create(vals)
        if res.date >= fields.Date.today():
            res.next_date = res.date
        else:
            res.next_date = res._get_next_date(res.date, res.interval_number, res.interval_type)
        return res

    def write(self, vals):
        res = super(VttContactAnniversary, self).write(vals)
        if 'date' in vals or 'interval_number' in vals or 'interval_type' in vals:
            for e in self:
                e.next_date = e._get_next_date(e.date, e.interval_number, e.interval_type)
                e.is_planned = False
            activities = self.env['mail.activity'].search([
                ('date_deadline', '>', fields.Date.today()),
                ('anniversary_id', 'in', self.ids)
            ])
            if activities:
                activities.sudo().unlink()
            self._cron_next_activities()
        return res

    def _get_next_date(self, date, interval_number, interval_type):
        # d = fields.Datetime.from_string(date.strftime('%Y-%m-%d 12:00:00'))
        if interval_number <= 0:
            return date
        else:
            new_date = date
            type_map = {
                'day': 'days',
                'week': 'weeks',
                'month': 'months',
                'year': 'years'
            }
            params = {type_map[interval_type]: interval_number}
            while new_date < fields.Date.today():
                new_date = new_date + relativedelta(**params)
            return new_date

    def _cron_next_activities(self):
        # date_interval = self.env.user.company_id.vtt_anniversary_activity_interval or 0
        date_interval_param = self.env['ir.config_parameter'].sudo().get_param('vtt_contact_anniversary.anniversary_activity_interval', default='0')
        try:
            date_interval = int(date_interval_param)
        except ValueError:
            date_interval = 0
        if date_interval < 0:
            date_interval = 0
        next_date = fields.Date.today() + relativedelta(days=date_interval)
        events = self.search([
            ('next_date', '>=', fields.Date.today()),
            ('next_date', '<=', next_date),
            ('is_planned', '=', False),
            ('category_id', '!=', False)
        ])
        if events:
            # partners = events.partner_id
            vals_lst = []
            company = self.env['res.company'].sudo().search([], limit=1)
            for e in events:
                if e.category_id and e.category_id.activity_type_id:
                    vals = {
                        'summary': e.category_id.activity_summary or e.name,
                        'activity_type_id': e.category_id.activity_type_id.id,
                        'res_model_id': e.env['ir.model'].search([('model', '=', 'res.partner')], limit=1).id,
                        'res_id': e.partner_id.id,
                        'date_deadline': e.next_date,
                        'anniversary_id': e.id,
                    }
                    if e.partner_id.user_id:
                        vals['user_id'] = e.partner_id.user_id.id
                    else:
                        vals['user_id'] = SUPERUSER_ID

                    vals_lst.append(vals)
            if vals_lst:
                self.env['mail.activity'].sudo().create(vals_lst)
                events.filtered(lambda e: e.category_id).write({'is_planned': True})
        return True

    @api.model
    def _cron_next_date_activity(self):
        self._cron_next_date()
        self._cron_next_activities()


class VttContactAnniversaryCategory(models.Model):
    _name = 'vtt.contact.anniversary.category'
    _description = 'Contact Anniversary Category'

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)

    interval_number = fields.Integer('Recurrent', default=1)
    interval_type = fields.Selection([
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
        ('year', 'Year')
    ], 'Recurrent Type', required=True, default='year')

    activity_type_id = fields.Many2one('mail.activity.type', 'Activity')

    activity_summary = fields.Char('Activity Summary')
