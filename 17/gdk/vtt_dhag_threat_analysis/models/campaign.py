# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
# from . import analysis_tools


class InvestigateCampaign(models.Model):
    _name = 'investigate.campaign'
    _description = 'Investigate Campaign'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_from desc'

    name = fields.Char('Name', compute='_compute_name', store=True)
    date_from = fields.Date('From')
    date_to = fields.Date('To')

    location_id = fields.Many2one('investigate.location', 'Location')

    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)
    # Users
    user_ids = fields.Many2many('res.users', string='Users')

    description = fields.Html('Description')
    code = fields.Char('Campaign Code')

    # Reference to Investigate
    investigate_ids = fields.One2many('investigate.investigate', 'campaign_id', 'Investigates')

    # ss_code = fields.Char('Secret Sequence', copy=False)

    @api.depends('location_id', 'date_from')
    def _compute_name(self):
        for campaign in self:
            year = campaign.date_from and campaign.date_from.year or fields.Date.today().year
            loc = campaign.location_id and f'{campaign.location_id.country_id.code}.{campaign.location_id.name}' or ''
            campaign.name = f'{year}.{loc}'

    @api.onchange('location_id', 'date_from')
    def _onchange_location_id(self):
        if self.date_from:
            year = self.date_from.year
        else:
            year = fields.Date.today().year
        if self.location_id:
            loc = f'{self.location_id.country_id.code}.{self.location_id.name}'
        else:
            loc = ''

        self.name = f'{year}.{loc}'