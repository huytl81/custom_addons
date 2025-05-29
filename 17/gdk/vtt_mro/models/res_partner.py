#-*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    repair_order_count = fields.Integer('Repair Count', compute='_compute_repair_order_count')
    maintenance_plan_count = fields.Integer('Maintenance Count', compute='_compute_maintenance_plan_count')
    warranty_ticket_count = fields.Integer('Warranty Count', compute='_compute_warranty_ticket_count')

    maintenance_plan_this_month = fields.Boolean(compute='_compute_maintenance_plan_this_month',
                                                 search='_search_value_maintenance_plan_this_month')
    maintenance_plan_next_month = fields.Boolean(compute='_compute_maintenance_plan_this_month',
                                                 search='_search_value_maintenance_plan_next_month')

    def _compute_maintenance_plan_this_month(self):
        month_start = fields.Datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_next = fields.Datetime.now().replace(month=fields.Datetime.now().month+1, day=1, hour=0, minute=0, second=0, microsecond=0)
        month_stop = fields.Datetime.now().replace(month=fields.Datetime.now().month+2, day=1, hour=0, minute=0, second=0, microsecond=0)
        this_month = self.env['vtt.maintenance.plan'].search([
            ('state', '=', 'run'),
            ('partner_id', '!=', False),
            ('dt_plan', '>=', month_start),
            ('dt_plan', '<', month_next)
        ])
        next_month = self.env['vtt.maintenance.plan'].search([
            ('state', '=', 'run'),
            ('partner_id', '!=', False),
            ('dt_plan', '>=', month_next),
            ('dt_plan', '<', month_stop)
        ])
        this_month_partners = this_month.mapped('partner_id')
        next_month_partners = next_month.mapped('partner_id')
        for p in self:
            p.maintenance_plan_this_month = p in this_month_partners
            p.maintenance_plan_next_month = p in next_month_partners

    @api.model
    def _search_value_maintenance_plan_this_month(self, operator, value):
        recs = self.search([]).filtered(lambda p: p.maintenance_plan_this_month is True)

        return [('id', 'in', [x.id for x in recs])]

    @api.model
    def _search_value_maintenance_plan_next_month(self, operator, value):
        recs = self.search([]).filtered(lambda p: p.maintenance_plan_next_month is True)

        return [('id', 'in', [x.id for x in recs])]

    def _compute_repair_order_count(self):
        order_read_group = self.env['vtt.repair.order']._read_group(
            [('partner_id', '!=', False)],
            ['partner_id'],
            ['__count'])
        result = {partner_id.id: count for partner_id, count in order_read_group}
        for partner in self:
            partner.repair_order_count = result.get(partner.id, 0)

    def _compute_maintenance_plan_count(self):
        plan_read_group = self.env['vtt.maintenance.plan']._read_group(
            [('partner_id', '!=', False), ('state', '=', 'run')],
            ['partner_id'],
            ['__count'])
        result = {partner_id.id: count for partner_id, count in plan_read_group}
        for partner in self:
            partner.maintenance_plan_count = result.get(partner.id, 0)

    def _compute_warranty_ticket_count(self):
        warranty_read_group = self.env['vtt.warranty.ticket']._read_group(
            [('partner_id', '!=', False), ('state', '=', '1_valid')],
            ['partner_id'],
            ['__count'])
        result = {partner_id.id: count for partner_id, count in warranty_read_group}
        for partner in self:
            partner.warranty_ticket_count = result.get(partner.id, 0)

    def action_view_maintenance(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('vtt_mro.vtt_act_window_maintenance_plan')
        action['domain'] = [('partner_id', '=', self.id)]
        context = {
            'default_partner_id': self.id,
        }
        action['context'] = context
        return action

    def action_view_repair(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id("vtt_mro.vtt_act_window_repair_order")
        action['domain'] = [('partner_id', '=', self.id)]
        context = {
            'default_partner_id': self.id,
        }
        action['context'] = context
        return action

    def action_view_warranty(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id("vtt_mro.vtt_act_window_warranty_ticket")
        action['domain'] = [('partner_id', '=', self.id)]
        context = {
            'default_partner_id': self.id,
        }
        action['context'] = context
        return action