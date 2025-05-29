# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID
from datetime import datetime, date, timedelta
import pytz
from korean_lunar_calendar import KoreanLunarCalendar


def get_valid_lunar_date(year, month, day):
    lunar_calendar = KoreanLunarCalendar()
    daystart = day
    lunar_calendar.setLunarDate(year, month, daystart, True)
    while not lunar_calendar.solarDay:
        daystart -= 1
        lunar_calendar.setLunarDate(year, month, daystart, True)
    next_date = date(lunar_calendar.solarYear, lunar_calendar.solarMonth, lunar_calendar.solarDay)
    return next_date


class LandTombSlot(models.Model):
    _name = 'vtt.land.tomb.slot'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Tomb Slot'

    internal_ref = fields.Char('Ref.')

    tomb_id = fields.Many2one('vtt.land.tomb', 'Tomb')
    plot_id = fields.Many2one('vtt.land.plot', 'Plot')

    dead_id = fields.Many2one('res.partner', 'Dead')
    gender = fields.Selection(related='dead_id.gender', store=True)
    dob = fields.Date('Birthday', compute='_compute_dead_id_date', store=True)
    dod = fields.Date('Dead day', compute='_compute_dead_id_date', store=True)
    age = fields.Integer('Age', compute='_compute_age', store=True)

    dod_lunar_year = fields.Char('Lunar Dead Year', compute='_compute_dead_day_lunar', store=True)
    dod_lunar_month = fields.Char('Lunar Dead Month', compute='_compute_dead_day_lunar', store=True)
    dod_lunar_day = fields.Char('Lunar Dead Day', compute='_compute_dead_day_lunar', store=True)
    dod_lunar_str = fields.Char('Lunar Dead Date', compute='_compute_dead_day_lunar', store=True)

    dod_lunar_warning = fields.Boolean('Lunar Dead Warning', compute='_compute_lunar_dead_warning')

    dod_next_anniversary = fields.Date('Next Anniversary', compute='_compute_next_anniversary', store=True)
    dod_next_anniversary_lunar_str = fields.Char('Next Anniversary Lunar', compute='_compute_next_anniversary_lunar', store=True)

    dirt_fill_type = fields.Selection([
        ('none', 'None'),
        ('sand', 'Sand'),
        ('dirt', 'Dirt')
    ], 'Dirt Fill Type', default='none')

    available_check = fields.Boolean('Available?', compute='_compute_available_check', store=True)

    date_receipt = fields.Date('Receipt Date')
    time_receipt = fields.Float('Receipt Time')
    dt_receipt = fields.Datetime('Receipt Datetime', compute='_compute_receipt_datetime', store=True)

    def _compute_next_anniversary(self):
        today = fields.Date.today()
        for ts in self:
            if ts.dod:
                year = today.year
                next_date = get_valid_lunar_date(year, int(ts.dod_lunar_month), int(ts.dod_lunar_day))
                if next_date < date.today():
                    year += 1
                    next_date = get_valid_lunar_date(year, int(ts.dod_lunar_month), int(ts.dod_lunar_day))
                ts.dod_next_anniversary = next_date
            else:
                ts.dod_next_anniversary = False

    @api.depends('dod_next_anniversary')
    def _compute_next_anniversary_lunar(self):
        lunar_calendar = KoreanLunarCalendar()
        for ts in self:
            if ts.dod_next_anniversary:
                anni = ts.dod_next_anniversary
                lunar_stamp = _("Lunar Day")
                lunar_calendar.setSolarDate(anni.year, anni.month, anni.day)
                ts.dod_next_anniversary_lunar_str = f'{lunar_calendar.lunarDay}/{lunar_calendar.lunarMonth} {lunar_stamp}'
            else:
                ts.dod_next_anniversary_lunar_str = ''

    @api.depends('dod')
    def _compute_dead_day_lunar(self):
        lunar_calendar = KoreanLunarCalendar()
        for ts in self:
            if ts.dod:
                lunar_calendar.setSolarDate(ts.dod.year, ts.dod.month, ts.dod.day)
                ts.dod_lunar_year = lunar_calendar.lunarYear
                ts.dod_lunar_month = lunar_calendar.lunarMonth
                ts.dod_lunar_day = lunar_calendar.lunarDay
                ts.dod_lunar_str = f'{lunar_calendar.lunarDay}/{lunar_calendar.lunarMonth} {_("Lunar Day")}'
            else:
                ts.dod_lunar_year = ''
                ts.dod_lunar_month = ''
                ts.dod_lunar_day = ''
                ts.dod_lunar_str = ''

    def _compute_lunar_dead_warning(self):
        today = fields.Date.today()
        for ts in self:
            ts._compute_next_anniversary()
            if ts.dod_next_anniversary:
                warn_date = ts.dod_next_anniversary + timedelta(days=-15)
                if today >= warn_date:
                    ts.dod_lunar_warning = True
                else:
                    ts.dod_lunar_warning = False
            else:
                ts.dod_lunar_warning = False

    @api.depends('dead_id', 'dead_id.dob', 'dead_id.dod')
    def _compute_dead_id_date(self):
        for ts in self:
            if ts.dead_id:
                ts.dob = ts.dead_id.dob
                ts.dod = ts.dead_id.dod

    @api.depends('dob', 'dod')
    def _compute_age(self):
        for ts in self:
            age = 0
            if ts.dob:
                if ts.dod:
                    age = ts.dod.year - ts.dob.year
                else:
                    age = date.today().year - ts.dob.year
            ts.age = age

    @api.depends('date_receipt', 'time_receipt')
    def _compute_receipt_datetime(self):
        for ts in self:
            if not ts.date_receipt and not ts.time_receipt:
                ts.dt_receipt = False
            else:
                tm = ts.time_receipt or 0.0
                tzinfo = pytz.timezone(self.env.user.tz)
                ts.dt_receipt = ts.date_receipt
                offset = tzinfo.utcoffset(ts.dt_receipt)
                ts.dt_receipt += timedelta(minutes=tm*60) - offset

    @api.depends('dead_id')
    def _compute_available_check(self):
        for lts in self:
            check = True
            if lts.dead_id:
                check = False
            lts.available_check = check

    def name_get(self):
        result = []
        for ts in self:
            name = ''
            if ts.internal_ref:
                name += f'{ts.internal_ref} - '
            if ts.dead_id:
                ts_name = ts.dead_id.name
                ts_name += f' {ts.dob and ts.dob.year or "/"} - {ts.dod and ts.dod.year or "/"}'
            else:
                ts_name = _('Empty Slot')
            name += ts_name
            result.append((ts.id, name))
        return result

    def _notif_next_anniversary(self, user_id):
        month_param = int(self.env['ir.config_parameter'].sudo().get_param('vtt_lhv_next_anniversary_month_notif', default=1))
        values = {
            'month_param': month_param,
            'solar_calendar': self.dod_next_anniversary.strftime("%d/%m/%Y"),
            'lunar_calendar': self.dod_next_anniversary_lunar_str
        }
        note = self.env.ref('vtt_lhv_cemetery.tomb_slot_next_anniversary_notif')._render(values=values)
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            self.dod_next_anniversary,
            note=note,
            user_id=user_id,
        )

    @api.model
    def _cron_notif_next_anniversary(self):
        month_param = int(
            self.env['ir.config_parameter'].sudo().get_param('vtt_lhv_next_anniversary_month_notif', default=1))
        today = fields.Date.today()
        check_date_start = date(today.year, today.month, 1)
        check_date_end = date(today.year, today.month+month_param+1, 1)
        tss = self.search([('dod_next_anniversary', '>=', check_date_start), ('dod_next_anniversary', '<', check_date_end)])

        users = self.env.ref('vtt_lhv_cemetery.vtt_group_cemetery_care_service_manager').sudo().users.ids
        if not users:
            users = [SUPERUSER_ID]

        if tss:
            for ts in tss:
                for uid in users:
                    ts._notif_next_anniversary(uid)