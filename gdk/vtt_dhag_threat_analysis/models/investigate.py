# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from . import analysis_tools


class InvestigateInvestigate(models.Model):
    _name = 'investigate.investigate'
    _description = 'Investigate'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'threat.sync.mixin']
    _order = 'campaign_id, date desc'

    name = fields.Char('Name', compute='_compute_name', store=True)
    location_id = fields.Many2one('investigate.location', 'Location')
    campaign_id = fields.Many2one('investigate.campaign', 'Campaign')

    date = fields.Date('Date', default=fields.Date.today)

    @api.onchange('location_id')
    def onchange_location_campaign(self):
        if self.location_id:
            self.campaign_id = False

    @api.onchange('location_id', 'date', 'department', 'device_name')
    def _onchange_location_id(self):
        if self.date:
            year = self.date.year
        else:
            year = fields.Date.today().year
        if self.location_id:
            loc = f'{self.location_id.country_id.code}.{self.location_id.name}'
        else:
            loc = ''
        if self.department or self.device_name:
            device = f'{self.department}.{self.device_name}'
        else:
            device = ''

        self.name = f'{year}.{loc}.{device}'

    @api.depends('location_id', 'date', 'department', 'device_name')
    def _compute_name(self):
        for invest in self:
            year = invest.date and invest.date.year or fields.Date.today().year
            loc = invest.location_id and f'{invest.location_id.country_id.code}.{invest.location_id.name}' or ''
            device = (invest.department or invest.device_name) and f'{invest.department}.{invest.device_name}' or ''
            invest.name = f'{year}.{loc}.{device}'

    use_person = fields.Char('User')
    department = fields.Char('Department', compute='_compute_department', store=True)
    # Department Suggestion
    department_suggest_id = fields.Many2one('investigate.department.suggest', 'Department')

    @api.onchange('department_suggest_id')
    def onchange_department_suggest(self):
        for i in self:
            i.department = i.department_suggest_id.name

    @api.depends('department_suggest_id')
    def _compute_department(self):
        for invest in self:
            invest.department = invest.department_suggest_id.name

    device_name = fields.Char('Device Name')

    user_id = fields.Many2one('res.users', 'Investigator', default=lambda self: self.env.user)

    # Device Information
    device_information = fields.Html('Device Information')
    operation_system = fields.Char('Operation System')
    softwares = fields.Html('Softwares')
    connect_type = fields.Selection([
        ('internet', 'Internet'),
        ('LAN', 'LAN'),
        ('none', 'None')
    ], 'Connection Type', default='internet')
    device_type = fields.Selection([
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C')
    ], 'Device Type', default='A')

    preliminary_summary = fields.Html('Preliminary')

    investigate_malware_ids = fields.One2many('investigate.malware', 'investigate_id', 'Malwares')

    confirm_count = fields.Integer('Confirmed', compute='_compute_malware_state_count')
    doubt_count = fields.Integer('Doubt', compute='_compute_malware_state_count')
    state_count_overview = fields.Char('Overview', compute='_compute_malware_state_count')

    def _compute_malware_state_count(self):
        for ii in self:
            malwares = ii.mapped('investigate_malware_ids')
            confirmed = malwares.filtered(lambda x: x.state == 'confirm')
            doubt = malwares.filtered(lambda x: x.state == 'doubt')
            ii.confirm_count = len(confirmed)
            ii.doubt_count = len(doubt)
            ii.state_count_overview = f'{len(confirmed)}/ {len(malwares)}'

    # Activities
    threat_activity_ids = fields.Many2many('threat.malware.activity.detail', 'investigate_threat_activity_detail_rel', string='Activities')

    # Directory to file or folder of samples
    sample_dir = fields.Char('Sample(s) Directory')

    ss_code = fields.Char('Secret Sequence', copy=False)

    # Comparison
    compare_ids = fields.One2many('threat.comparison', 'investigate_id', 'Comparison')
    compare_count = fields.Integer('# Compare Reports', compute='_compute_compare_count')

    def _compute_compare_count(self):
        for i in self:
            i.compare_count = len(i.compare_ids)

    @api.onchange('campaign_id')
    def onchange_campaign(self):
        if self.campaign_id:
            self.location_id = self.campaign_id.location_id

    def import_lastline_report_wz(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Lastline Report'),
            'view_mode': 'form',
            'res_model': 'lastline.report.import.wizard',
            'target': 'new',
        }

    def button_dummy(self):
        return True

    def view_comparison(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Comparison Report'),
            'view_mode': 'tree,form',
            'domain': [('type', '=', 'investigate.investigate'), ('investigate_id', '=', self.id)],
            'context': {'default_investigate_id': self.id, 'default_type': 'investigate.investigate', 'list_type': 'investigate'},
            'res_model': 'threat.comparison',
            'target': 'current',
        }


class InvestigateDepartmentSuggest(models.Model):
    _name = 'investigate.department.suggest'
    _description = 'Department Suggestion'

    name = fields.Char('Name', required=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Department name already exists!'),
    ]

    def _prepare_push_data(self):
        departments = self.search([])
        return {'departments': [d.name for d in departments]}

    def extract_sync_data(self, datas, type='push'):
        if datas and datas.get('departments'):
            r_names = datas['departments']
            departments = self.search([('name', 'in', r_names)])
            o_names = [d.name for d in departments]
            crs = [{'name': d for d in r_names if d not in o_names}]
            crs_checked = [c for c in crs if c]
            if crs_checked:
                self.create(crs_checked)