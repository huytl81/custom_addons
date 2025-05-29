# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta
import pytz


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'vtt.custom.rating.mixin']

    lhv_order_type = fields.Selection([
        ('land_order', 'Land Order'),
        ('service_order', 'Service Order'),
    ], 'Order Type', default='service_order')

    can_confirm = fields.Boolean('Conferable?', compute='_compute_conferable')

    is_include_care_service = fields.Boolean('Included Care Service', compute='_compute_include_care_service', store=True)
    is_include_land_product = fields.Boolean('Included Land Product', compute='_compute_include_care_service', store=True)

    land_plot_ids = fields.Many2many('vtt.land.plot', 'sale_order_land_plot_rel', string='Plots', compute='_compute_land_plot_ids', store=True)

    partner_contact_ids = fields.Many2many('res.partner', string='Contacts')

    land_contract_id = fields.Many2one('vtt.land.contract', 'Land Contract')

    # Care service receipt date
    # vtt_date_receipt = fields.Date('Receipt Date')
    # vtt_time_receipt = fields.Float('Receipt Time')
    # vtt_dt_receipt = fields.Datetime('Receipt Datetime', compute='_compute_receipt_datetime', store=True)

    # @api.depends('vtt_date_receipt', 'vtt_time_receipt')
    # def _compute_receipt_datetime(self):
    #     for ts in self:
    #         if not ts.vtt_date_receipt and not ts.vtt_time_receipt:
    #             ts.vtt_dt_receipt = False
    #         else:
    #             tm = ts.time_receipt or 0.0
    #             tzinfo = pytz.timezone(self.env.user.tz)
    #             ts.vtt_dt_receipt = ts.date_receipt
    #             offset = tzinfo.utcoffset(ts.vtt_dt_receipt)
    #             ts.vtt_dt_receipt += timedelta(minutes=tm * 60) - offset

    @api.onchange('land_contract_id')
    def onchange_land_contract_id(self):
        if self.land_contract_id and self.land_contract_id.partner_id:
            self.partner_id = self.land_contract_id.partner_id

    @api.depends('order_line', 'order_line.land_plot_id')
    def _compute_land_plot_ids(self):
        for so in self:
            lines = so.mapped('order_line')
            plots = lines.land_plot_id
            so.land_plot_ids = plots

    @api.depends('order_line', 'order_line.product_id')
    def _compute_include_care_service(self):
        for so in self:
            check_care_service = False
            check_land = False
            if so.order_line:
                if any(line.product_id.is_care_service for line in so.order_line):
                    check_care_service = True
                if any(line.product_id.is_land for line in so.order_line):
                    check_land = True
            so.is_include_care_service = check_care_service
            so.is_include_land_product = check_land

    def _compute_conferable(self):
        for so in self:
            check = False
            if so.state in ['sent']:
                sale_lines = so.mapped('order_line')
                if all(not s.product_id.is_land for s in sale_lines):
                    check = True
                else:
                    land_lines = sale_lines.filtered(lambda x: x.product_id.is_land)
                    if all(s.land_plot_state == 'approved' for s in land_lines):
                        check = True
            so.can_confirm = check

    def action_quotation_send(self):
        res = super(SaleOrder, self).action_quotation_send()
        sale_lines = self.mapped('order_line').filtered(lambda x: x.product_id.is_land and x.land_plot_id)
        for s in sale_lines:
            if s.land_plot_state == 'draft':
                s.land_plot_state = 'interest'
        sale_lines.land_plot_id.update_plot_state()
        return res

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        sale_lines = self.mapped('order_line').filtered(lambda x: x.product_id.is_land and x.land_plot_id)
        for s in sale_lines:
            s.land_plot_state = 'draft'
        sale_lines.land_plot_id.update_plot_state()
        return res

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        sale_lines = self.mapped('order_line').filtered(lambda x: x.product_id.is_land and x.land_plot_id)
        for s in sale_lines:
            s.land_plot_state = 'sold'
            # # s.land_plot_id.update_plot_state()
            # # Create contract
            # contract_vals = {
            #     'partner_id': self.partner_id.id,
            #     'plot_id': s.land_plot_id.id,
            #     'date': self.date_order,
            #     'order_id': self.id,
            # }
            # seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(self.date_order))
            # contract_name = self.env['ir.sequence'].next_by_code('vtt.land.contract', sequence_date=seq_date) or _('New')
            # contract_vals['name'] = contract_name
            # s.land_plot_id.contract_id = self.env['vtt.land.contract'].create(contract_vals)
            if s.order_id.land_contract_id:
                s.land_plot_id.contract_id = s.order_id.land_contract_id
        sale_lines.land_plot_id.update_plot_state()
        return res

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if 'state' in vals:
            sale_lines = self.mapped('order_line').filtered(lambda x: x.product_id.is_land and x.land_plot_id)
            for s in sale_lines:
                if vals['state'] in ['draft', 'cancel']:
                    s.land_plot_state = 'draft'
                elif vals['state'] == 'sent':
                    s.land_plot_state = 'interest'
                elif vals['state'] == 'sale':
                    s.land_plot_state == 'sold'
            sale_lines.land_plot_id.update_plot_state()
        return res

    def create_subscriptions(self):
        res = []
        for order in self:
            to_create = order._split_subscription_lines()
            # create a subscription for each template with all the necessary lines
            for template in to_create:
                values = order._prepare_subscription_data(template)
                land_plots = to_create[template].mapped('land_plot_id')
                lst_subs_data = [to_create[template].filtered(lambda l: not l.land_plot_id)]
                if land_plots:
                    for land_plot in land_plots:
                        lst_subs_data.append(to_create[template].filtered(lambda l: l.land_plot_id == land_plot))
                for subs_data_line in lst_subs_data:
                    values['recurring_invoice_line_ids'] = subs_data_line._prepare_subscription_line_data()
                    subscription = self.env['sale.subscription'].sudo().create(values)
                    subscription.onchange_date_start()
                    subscription.write({
                        'land_plot_id': subs_data_line.mapped('land_plot_id').id
                    })
                    res.append(subscription.id)
                    subs_data_line.write({'subscription_id': subscription.id})
                    subscription.message_post_with_view(
                        'mail.message_origin_link', values={'self': subscription, 'origin': order},
                        subtype_id=self.env.ref('mail.mt_note').id, author_id=self.env.user.partner_id.id
                    )
                    self.env['sale.subscription.log'].sudo().create({
                        'subscription_id': subscription.id,
                        'event_date': fields.Date.context_today(self),
                        'event_type': '0_creation',
                        'amount_signed': subscription.recurring_monthly,
                        'recurring_monthly': subscription.recurring_monthly,
                        'currency_id': subscription.currency_id.id,
                        'category': subscription.stage_category,
                        'user_id': order.user_id.id,
                        'team_id': order.team_id.id,
                    })
        return res

    def _get_custom_rating_context(self):
        context = super(SaleOrder, self)._get_custom_rating_context()
        context.update({
            'default_partner_id': self.partner_id.id,
            'default_user_id': self.user_id.id
        })
        return context