# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta
import json


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    land_plot_id = fields.Many2one('vtt.land.plot', 'Plot')
    is_land_product = fields.Boolean('Is Land Product', related='product_id.is_land')

    land_plot_state = fields.Selection([
        ('draft', 'Draft'),
        ('interest', 'Interest'),
        ('reserved', 'Reserved'),
        ('approved', 'Approved'),
        ('sold', 'Sold')
    ], 'Land State', default='draft')

    can_land_reserved = fields.Boolean('Reservable?', compute='_compute_land_reservable', store=True)

    is_care_service_product = fields.Boolean('Is Care Service Product', related='product_id.is_care_service')

    dt_land_reserved = fields.Datetime('Reserved Date')
    dt_land_approve = fields.Datetime('Approved Date')

    land_slot_id = fields.Many2one('vtt.land.tomb.slot', 'Tomb Slot')

    product_id_domain = fields.Char('Product Domain', compute='_compute_product_id_domain')

    @api.onchange('land_plot_id')
    def onchange_land_plot_id(self):
        if self.land_plot_id and self.land_plot_id.lst_price:
            self.price_unit = self.land_plot_id.lst_price

    @api.depends('order_id.lhv_order_type', 'order_id.company_id')
    def _compute_product_id_domain(self):
        for line in self:
            if line.order_id.lhv_order_type in ['land_order']:
                domain = [('is_land', '!=', False), ('sale_ok', '=', True), '|',
                          ('company_id', '=', False), ('company_id', '=', line.order_id.company_id.id)]
            else:
                domain = [('is_land', '=', False), ('sale_ok', '=', True), '|',
                          ('company_id', '=', False), ('company_id', '=', line.order_id.company_id.id)]
            line.product_id_domain = json.dumps(domain)

    @api.depends('land_plot_id', 'land_plot_id.state', 'state')
    def _compute_land_reservable(self):
        for s in self:
            check = False
            if s.state in ['sent'] and s.land_plot_id:
                if s.land_plot_id.state in ['open', 'interest']:
                    check = True
            s.can_land_reserved = check

    def action_plot_reserved(self):
        self.write({
            'land_plot_state': 'reserved',
            'dt_land_reserved': fields.Datetime.now()
        })
        self.land_plot_id.update_plot_state()
        return

    def action_plot_release(self):
        self.write({
            'land_plot_state': 'interest',
            'dt_land_reserved': False,
            'dt_land_approve': False
        })
        self.land_plot_id.update_plot_state()
        return

    def action_plot_approve(self):
        self.write({
            'land_plot_state': 'approved',
            'dt_land_approve': fields.Datetime.now()
        })
        self.land_plot_id.update_plot_state()
        return

    def _cron_land_plot_unreserved(self):
        day_param = int(self.env['ir.config_parameter'].sudo().get_param('vtt_lhv_land_plot_day_unreserved', default=3))
        today = fields.Date.today()
        check_day = today - timedelta(day_param)
        reserves = self.search([
            ('state', 'in', ['sent']),
            ('land_plot_id', '!=', False),
            ('land_plot_state', 'in', ['reserved']),
            ('dt_land_reserved', '<=', check_day)
        ])
        if reserves:
            for so_line in reserves:
                check = True
                if not so_line.order_id.invoice_ids or any(inv.state not in ['not_paid'] for inv in so_line.order_id.invoice_ids):
                    check = False
                if check:
                    so_line.action_plot_release()
