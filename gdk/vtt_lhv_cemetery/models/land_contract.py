# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VttLandContract(models.Model):
    _name = 'vtt.land.contract'
    _description = 'Land Contract'
    _inherit = ['vtt.custom.rating.mixin', 'mail.thread', 'mail.activity.mixin']
    # _inherit = ['vtt.custom.rating.mixin']

    plot_id = fields.Many2one('vtt.land.plot', 'Plot')
    plot_ids = fields.One2many('vtt.land.plot', 'contract_id', 'Plots')
    name = fields.Char('Name')

    date = fields.Date('Date')

    partner_id = fields.Many2one('res.partner', 'Partner')
    partner_phone = fields.Char(related='partner_id.phone')
    partner_mobile = fields.Char(related='partner_id.mobile')
    partner_email = fields.Char(related='partner_id.email')
    contact_ids = fields.Many2many('res.partner', 'land_contract_partner_contact_rel', string='Contacts')

    order_id = fields.Many2one('sale.order', 'Sale Order')
    order_ids = fields.One2many('sale.order', 'land_contract_id', 'Sale Orders')
    subscription_ids = fields.One2many('sale.subscription', 'land_contract_id', 'Subscriptions')
    construct_ids = fields.One2many('vtt.construct', 'land_contract_id', 'Constructions')

    order_count = fields.Integer('Order Count', compute='_compute_order_count')
    subscription_count = fields.Integer('Subscription Count', compute='_compute_subscription_count')
    construct_count = fields.Integer('Construction Count', compute='_compute_construct_count')

    land_certificate_state = fields.Selection([
        ('new', 'No Certificate'),
        ('certificated', 'Certificated')
    ], 'Land Certificate State', default='new')
    land_certificate_date = fields.Date('Land Certificate Date')
    land_certificate = fields.Char('Land Certificate')

    def _compute_order_count(self):
        for contract in self:
            contract.order_count = len(contract.order_ids)

    def _compute_subscription_count(self):
        for contract in self:
            contract.subscription_count = len(contract.subscription_ids)

    def _compute_construct_count(self):
        for contract in self:
            contract.construct_count = len(contract.construct_ids)

    def _get_custom_rating_context(self):
        context = super(VttLandContract, self)._get_custom_rating_context()
        context.update({
            'default_partner_id': self.partner_id.id,
        })
        return context

    def view_sale_order(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action['domain'] = [('land_contract_id', '=', self.id)]
        action['context'] = {
            'default_lhv_order_type': 'service_order',
            'default_land_contract_id': self.id,
        }
        return action

    def view_sale_subscription(self):
        action = self.env["ir.actions.actions"]._for_xml_id("vtt_sale_subscription.sale_subscription_action")
        action['domain'] = [('land_contract_id', '=', self.id)]
        action['context'] = {
            'default_land_contract_id': self.id,
        }
        return action

    def view_construction(self):
        action = self.env["ir.actions.actions"]._for_xml_id("vtt_lhv_cemetery.vtt_act_window_construct")
        action['domain'] = [('land_contract_id', '=', self.id)]
        action['context'] = {
            'default_land_contract_id': self.id,
        }
        return action