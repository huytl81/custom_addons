# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID
from datetime import date, datetime


class MaintenancePlan(models.Model):
    _name = 'vtt.maintenance.plan'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Maintenance Plan'
    _order = 'dt_plan desc, partner_id, equipment_id'

    def _get_default_plan_type(self):
        types = self.env['vtt.maintenance.plan.type'].search([('period_type', '=', 'month')]).sorted(lambda t: t.period_value)
        return types and types[0] or False

    name = fields.Char('Reference', default=_('New'))

    equipment_id = fields.Many2one('vtt.equipment.equipment', 'Equipment', tracking=2)
    equipment_model_name = fields.Char('Model', related='equipment_id.model_name')
    equipment_manufacture = fields.Char('Manufacture', related='equipment_id.manufacture')
    equipment_manufacture_year = fields.Char('Year', related='equipment_id.manufacture_year')
    equipment_serial_number = fields.Char('Serial Number', related='equipment_id.serial_number')

    equipment_date_warranty = fields.Date('Warranty', related='equipment_id.date_warranty')

    partner_id = fields.Many2one('res.partner', 'Partner', tracking=1)
    phone = fields.Char('Phone', related='partner_id.phone')
    email = fields.Char('Email', related='partner_id.email')

    type = fields.Selection([
        ('general', 'General'),
        ('parts', 'Parts'),
    ], 'Type', default='general', tracking=4)
    product_id = fields.Many2one('product.product', 'Related Part', tracking=4)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('run', 'Run'),
        ('close', 'Close'),
    ], 'Status', default='draft', tracking=3)

    note = fields.Html('Note')

    plan_type_id = fields.Many2one('vtt.maintenance.plan.type', 'Plan Type', required=True, default=_get_default_plan_type, tracking=5)
    dt_last = fields.Datetime('Last Date', default=fields.Datetime.now)
    dt_plan = fields.Datetime('Planned Date', tracking=6)

    need_renew = fields.Boolean('Need Renew', compute='_compute_need_renew')
    plan_this_month = fields.Boolean(compute='_compute_plan_this_month',
                                     search='_value_search_plan_this_month')
    plan_next_month = fields.Boolean(compute='_compute_plan_next_month',
                                     search='_value_search_plan_next_month')

    def _compute_plan_this_month(self):
        month_start = fields.Datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_stop = fields.Datetime.now().replace(month=fields.Datetime.now().month+1, day=1, hour=0, minute=0, second=0, microsecond=0)
        for p in self:
            if p.dt_plan >= month_start and p.dt_plan < month_stop:
                p.plan_this_month = True
            else:
                p.plan_this_month = False

    @api.model
    def _value_search_plan_this_month(self, operator, value):
        recs = self.search([]).filtered(lambda p: p.plan_this_month is True)

        return [('id', 'in', [x.id for x in recs])]

    def _compute_plan_next_month(self):
        month_start = fields.Datetime.now().replace(month=fields.Datetime.now().month+1, day=1, hour=0, minute=0, second=0, microsecond=0)
        month_stop = fields.Datetime.now().replace(month=fields.Datetime.now().month+2, day=1, hour=0, minute=0, second=0, microsecond=0)
        for p in self:
            if p.dt_plan >= month_start and p.dt_plan < month_stop:
                p.plan_next_month = True
            else:
                p.plan_next_month = False

    @api.model
    def _value_search_plan_next_month(self, operator, value):
        recs = self.search([]).filtered(lambda p: p.plan_next_month is True)

        return [('id', 'in', [x.id for x in recs])]

    def _compute_need_renew(self):
        for p in self:
            if p.state in ('run') and p.dt_plan <= fields.Datetime.now():
                p.need_renew = True
            else:
                p.need_renew = False

    def action_start_plan(self):

        return self.write({
            'state': 'run'
        })

    def action_close_plan(self):

        return self.write({
            'state': 'close'
        })

    def renew_plan_by_last(self):
        for p in self:
            p_next = p.plan_type_id.get_next_by_period(p.dt_plan)
            while p_next <= fields.Datetime.now():
                p_next = p.plan_type_id.get_next_by_period(p_next)
            p.dt_last = p.dt_plan
            p.dt_plan = p_next

    def renew_plan_by_now(self):
        for p in self:
            p_next = p.plan_type_id.get_next_by_now(fields.Datetime.now())
            p.dt_last = p.dt_plan
            p.dt_plan = p_next

    @api.onchange('plan_type_id')
    def onchange_plan_type_id(self):
        if self.plan_type_id:
            dt_next = self.plan_type_id.get_next_by_period(fields.Datetime.now())
            self.dt_plan = dt_next

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("New")) == _("New"):
                # seq_date = fields.Datetime.context_timestamp(
                #     self, fields.Datetime.to_datetime(vals['dt_order'])
                # ) if 'dt_order' in vals else None
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'maintenance.plan', sequence_date=None) or _("New")

        return super().create(vals_list)

    @api.model
    def notify_next_maintenance_plan(self):
        # .with_user(SUPERUSER_ID)
        this_month = self.search([])
        this_month_p = this_month.mapped('partner_id')
        # this_month_origin = {p_id: this_month.filtered(lambda p: p.partner_id == p_id) for p_id in this_month_p}
        this_month_origin = [{'partner_id': p_id, 'plan_ids': this_month.filtered(lambda p: p.partner_id == p_id)} for p_id in this_month_p]
        mro_channel = self.env.ref('vtt_mro.vtt_channel_mro_team')
        all_mro_users = self.env.ref('vtt_mro.vtt_group_mro_user').users
        # notification_ids = [(0, 0, {
        #     'res_partner_id': u.partner_id.id,
        #     'notification_type': 'inbox'}) for u in all_mro_users]
        message = "Go fuck these girls with curves all the way and all holes!!!"
        # mro_channel.message_post(author_id=SUPERUSER_ID,
        #                          body=(message),
        #                          message_type='notification',
        #                          subtype_xmlid="mail.mt_comment",
        #                          # notification_ids=notification_ids,
        #                          partner_ids=all_mro_users.ids,)
        mro_channel.message_post_with_source(
            # 'vtt_mro.vtt_template_message_maintenance_month_reminder',
            'mail.message_origin_link',
            # render_values={'self': mro_channel, 'origin': this_month_origin},
            render_values={'self': mro_channel, 'origin': this_month},
            subtype_xmlid='mail.mt_note',
            # subtype_xmlid='mail.mt_comment',
        )