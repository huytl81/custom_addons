# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SupplyRequest(models.Model):
    _name = 'vtt.supply.request'
    _description = 'Supply Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_warehouse(self):
        wh = self.env.user._get_default_warehouse_id()
        return wh

    name = fields.Char('Reference', default=lambda self: _('New'), copy=False, index='trigram', readonly=True)
    company_id = fields.Many2one('res.company', "Company", required=True, readonly=True,
                                 default=lambda self: self.env.company)

    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse',)
    location_dest_id = fields.Many2one('stock.location', 'Destination Location')
    # procurement_group_id = fields.Many2one('procurement.group', 'Procurement Group', copy=False)

    picking_ids = fields.One2many('stock.picking', 'req_id', string='Transfers')
    picking_count = fields.Integer(string='Delivery Orders', compute='_compute_picking_count')
    need_picking = fields.Boolean('Need Picking?', compute='_compute_need_picking')

    request_user_id = fields.Many2one('res.users', 'Requester',
                                      default=lambda self: self.env.user)
    date = fields.Datetime('Creation Date', default=fields.Datetime.now)
    date_deadline = fields.Datetime('Deadline')
    date_done = fields.Datetime('Done Time')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('request', 'Request'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
    ], 'Status', default='draft', required=True)

    line_ids = fields.One2many('vtt.supply.request.line', 'request_id', 'Details')

    note = fields.Html('Note')

    purchase_ids = fields.One2many('purchase.order', 'req_id', 'Purchase')
    purchase_count = fields.Integer('Purchase Orders', compute='_compute_purchase_count')

    @api.depends('purchase_ids')
    def _compute_purchase_count(self):
        for req in self:
            req.purchase_count = len(req.purchase_ids)

    @api.depends('line_ids', 'line_ids.product_uom_qty', 'line_ids.qty_delivered', 'line_ids.qty_picking', 'state')
    def _compute_need_picking(self):
        for req in self:
            need_picking = False
            if req.state == 'confirm':
                if any(l.product_uom_qty > l.qty_picking for l in req.line_ids):
                    need_picking = True
            req.need_picking = need_picking

    def action_confirm(self):
        return self.write({
            'state': 'confirm'
        })

    def action_request(self):
        return self.write({
            'state': 'request'
        })

    def action_draft(self):
        return self.write({
            'state': 'draft',
        })

    def action_done(self):
        return self.write({
            'state': 'done',
            'date_done': fields.Datetime.now(),
        })

    def action_cancel(self):
        return self.write({
            'state': 'cancel',
            'date_done': False
        })

    @api.depends('picking_ids')
    def _compute_picking_count(self):
        for req in self:
            req.picking_count = len(req.picking_ids)

    def action_view_picking(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        pickings = self.picking_ids

        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
        # Prepare the context.
        picking_id = pickings.filtered(lambda l: l.picking_type_id.code == 'internal')
        if picking_id:
            picking_id = picking_id[0]
        else:
            picking_id = pickings[0]
        action['context'] = dict(self._context,
                                 default_partner_id=self.request_user_id.partner_id.id,
                                 default_picking_type_id=picking_id.picking_type_id.id,
                                 default_origin=self.name,
                                 default_req_id=self.id)
        return action

    def action_view_purchase(self):
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_form_action")
        purchases = self.purchase_ids

        if len(purchases) > 1:
            action['domain'] = [('id', 'in', purchases.ids)]
        elif purchases:
            form_view = [(False, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = purchases.id
        # Prepare the context.
        action['context'] = dict(self._context,
                                 default_origin=self.name,
                                 default_req_id=self.id)
        return action

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])
            if vals.get('name', _("New")) == _("New"):
                seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(vals['date'])
                ) if 'dt_order' in vals else None
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'supply.request', sequence_date=seq_date) or _("New")

        return super().create(vals_list)

    def action_create_draft_purchase(self):
        product_lines = self.line_ids.filtered(lambda l: l.product_id)
        action = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_rfq')
        picking_type_id = self.warehouse_id.in_type_id
        action['context'] = {
            'default_req_id': self.id,
            'req_id': self.id,
            'default_origin': self.name,
            'origin': self.name,
            'default_picking_type_id': picking_type_id.id,
        }
        lines = [(0, 0, {
            'product_id': l.product_id.id,
            'product_qty': l.product_uom_qty,
        }) for l in product_lines]
        action['context']['default_order_line'] = lines
        action['view_mode'] = 'form'
        action['views'] = [(False, 'form')]
        # action['res_id'] = False
        return action

    def get_req_picking_vals(self):
        self.ensure_one()
        picking_type_id = self.warehouse_id.int_type_id
        return {
            'req_id': self.id,
            'origin': self.name,
            'date_deadline': self.date_deadline,
            'picking_type_id': picking_type_id.id,
            'partner_id': self.request_user_id.partner_id.id,
            'location_dest_id': self.location_dest_id.id,
        }

    def create_picking(self):
        if self.state == 'confirm':
            product_lines = self.line_ids.filtered(lambda l: l.product_id)
            picking_vals = self.get_req_picking_vals()
            moves = [(0, 0, line._prepare_delivery_amount()) for line in product_lines]
            picking_vals['move_ids_without_package'] = moves
            picking = self.env['stock.picking'].create(picking_vals)
            picking.action_confirm()

            self.action_view_picking()
