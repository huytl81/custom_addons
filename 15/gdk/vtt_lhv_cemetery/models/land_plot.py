# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class LandPlot(models.Model):
    _name = 'vtt.land.plot'
    _description = 'Land Plot'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name')
    place = fields.Char('Place Description')
    internal_ref = fields.Char('Ref.')
    description = fields.Text('Description')

    area = fields.Float('Area')
    land_direction = fields.Char('Land Direction')

    place_id = fields.Many2one('vtt.land.place', 'Place')

    tomb_ids = fields.One2many('vtt.land.tomb', 'plot_id', 'Tombs')
    tomb_count = fields.Integer('Tomb count', compute='_compute_tomb_count')

    def _compute_tomb_count(self):
        for pl in self:
            pl.tomb_count = len(pl.tomb_ids)

    slot_ids = fields.One2many('vtt.land.tomb.slot', 'plot_id', 'Slots')
    slot_count = fields.Integer('Slot count', compute='_compute_slot_count')
    slot_buried_count = fields.Integer('Slot Buried count', compute='_compute_slot_count')

    def _compute_slot_count(self):
        for pl in self:
            pl.slot_count = len(pl.slot_ids)
            pl.slot_buried_count = len(pl.slot_ids.filtered(lambda sl: sl.dead_id))

    contract_ids = fields.One2many('vtt.land.contract', 'plot_id', 'Contract')
    contract_id = fields.Many2one('vtt.land.contract', 'Contract')
    contract_partner_id = fields.Many2one('res.partner', 'Contract Partner', related='contract_id.partner_id')

    sale_line_ids = fields.One2many('sale.order.line', 'land_plot_id', 'Sale Line')
    interest_count = fields.Integer('Interest Count', compute='_compute_interest_count')

    construct_ids = fields.One2many('vtt.construct', 'plot_id', 'Construction')

    subscription_ids = fields.One2many('sale.subscription', 'land_plot_id', 'Subscriptions')
    subscription_count = fields.Integer('Subscription Count', compute='_compute_subscription_count')

    def _compute_subscription_count(self):
        for pl in self:
            pl.subscription_count = len(pl.subscription_ids)

    def _compute_interest_count(self):
        for pl in self:
            sale_lines = pl.mapped('sale_line_ids').filtered(lambda x: x.state not in ['draft', 'cancel'])
            pl.interest_count = len(sale_lines)

    state = fields.Selection([
        ('pending', 'Pending'),
        ('open', 'Open'),
        ('interest', 'Interest'),
        ('reserved', 'Reserved'),
        ('approved', 'Approved'),
        ('sold', 'Sold'),
    ], 'State', default='pending')

    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Very High')
    ], 'Priority', default='1')

    customer_card_ids = fields.One2many('vtt.land.customer.card', 'plot_id', 'Customer Cards')

    construction_state = fields.Selection([
        ('new', 'No Construction'),
        ('design_progress', 'Designing Progress'),
        ('construct_progress', 'Construction Progress'),
        # ('acceptance', 'Construction Acceptance'),
        ('done', 'Done')
    ], 'Construction State', compute='_compute_construction_state', store=True)

    lst_price = fields.Float('Sales Price', digits='Product Price')
    market_price = fields.Float('Market Price', digits='Product Price')

    @api.depends('construct_ids', 'construct_ids.stage_id', 'construct_ids.construct_stage_id')
    def _compute_construction_state(self):
        first_design_stage = self.env['vtt.construct.stage'].search([('stage_type', '=', 'design')], limit=1)
        first_construct_stage = self.env['vtt.construct.stage'].search([('stage_type', '=', 'construct')], limit=1)
        for pl in self:
            c_state = 'new'
            if pl.construct_ids:
                constructs = pl.mapped('construct_ids')
                done_constructs = constructs.filtered(lambda c: c.construct_stage_id.is_closed)
                design_constructs = constructs.filtered(lambda c: c.stage_id != first_design_stage and c.construct_stage_id == first_construct_stage)
                construct_constructs = constructs.filtered(lambda c: c.construct_stage_id != first_construct_stage and not c.construct_stage_id.is_closed)
                if done_constructs:
                    c_state = 'done'
                elif construct_constructs:
                    c_state = 'construct_progress'
                elif design_constructs:
                    c_state = 'design_progress'
            pl.construction_state = c_state

    def action_open(self):
        return self.write({
            'state': 'open'
        })

    def action_pending(self):
        return self.write({
            'state': 'pending'
        })

    def update_plot_state(self):
        for pl in self:
            sale_lines = pl.mapped('sale_line_ids').filtered(lambda x: x.state not in ['draft', 'cancel'])
            check_sold = [s for s in sale_lines if s.land_plot_state == 'sold']
            check_approved = [s for s in sale_lines if s.land_plot_state == 'approved']
            check_reserved = [s for s in sale_lines if s.land_plot_state == 'reserved']
            if sale_lines:
                if check_sold:
                    pl.state = 'sold'
                elif check_approved:
                    pl.state = 'approved'
                elif check_reserved:
                    pl.state = 'reserved'
                else:
                    pl.state = 'interest'
            else:
                pl.state = 'open'

    def view_list_tombs(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'vtt.land.tomb',
            'view_mode': 'tree,form',
            'domain': [('plot_id', '=', self.id)],
            'context': {'default_plot_id': self.id}
        }

    def view_list_sale_lines(self):
        tree_view_id = self.env.ref('vtt_lhv_cemetery.vtt_view_tree_sale_order_line_land_reserved').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.line',
            'view_mode': 'tree,form',
            'domain': [('land_plot_id', '=', self.id), ('state', 'not in', ['draft', 'cancel'])],
            'views': [(tree_view_id, 'tree'), (False, 'form')],
        }

    def view_plot_contract(self):
        # contracts = self.mapped('contract_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("vtt_lhv_cemetery.vtt_act_window_land_contract")
        if self.contract_id:
            form_view = [(self.env.ref('vtt_lhv_cemetery.vtt_view_form_land_contract').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = self.contract_id.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        # if len(contracts) > 1:
        #     action['domain'] = [('id', 'in', contracts.ids)]
        # elif len(contracts) == 1:
        #     form_view = [(self.env.ref('vtt_lhv_cemetery.vtt_view_form_land_contract').id, 'form')]
        #     if 'views' in action:
        #         action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        #     else:
        #         action['views'] = form_view
        #     action['res_id'] = contracts.id
        # else:
        #     action = {'type': 'ir.actions.act_window_close'}
        return action

    def view_plot_subscription(self):
        subscriptions = self.mapped('subscription_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("vtt_sale_subscription.sale_subscription_action")
        if len(subscriptions) > 1:
            action['domain'] = [('id', 'in', subscriptions.ids)]
        elif len(subscriptions) == 1:
            form_view = [(self.env.ref('vtt_sale_subscription.sale_subscription_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = subscriptions.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_unassigned_customer_card(self):
        customer_cards = self.mapped('customer_card_ids')
        customer_cards.action_unassigned()
        return True