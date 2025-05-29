# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Equipment(models.Model):
    _name = 'vtt.equipment.equipment'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Equipment'

    name = fields.Char('Name', tracking=1)
    model_name = fields.Char('Model', tracking=3)
    manufacture = fields.Char('Manufacture', tracking=3)
    serial_number = fields.Char('Serial Number')
    manufacture_year = fields.Char('Year')

    # Need store for tracking effect
    date_warranty = fields.Date('Warranty', compute='_get_warranty', inverse='_set_warranty')
    partner_id = fields.Many2one('res.partner', 'Partner', tracking=2)

    product_id = fields.Many2one('product.product', 'Related Product', tracking=5)
    # product_ids = fields.Many2many('product.product', 'equipment_product_product_rel', string='Parts')

    categ_id = fields.Many2one('vtt.equipment.categ', 'Category', tracking=3)

    repair_order_ids = fields.One2many('vtt.repair.order', 'equipment_id', 'Repairs')
    repair_order_count = fields.Integer('Repair Count', compute='_compute_repair_order_count')

    maintenance_plan_this_month = fields.Boolean(compute='_compute_maintenance_plan_this_month',
                                                 search='_search_value_maintenance_plan_this_month')
    maintenance_plan_next_month = fields.Boolean(compute='_compute_maintenance_plan_this_month',
                                                 search='_search_value_maintenance_plan_next_month')

    def _compute_maintenance_plan_this_month(self):
        month_start = fields.Datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_next = fields.Datetime.now().replace(month=fields.Datetime.now().month + 1, day=1, hour=0, minute=0,
                                                   second=0, microsecond=0)
        month_stop = fields.Datetime.now().replace(month=fields.Datetime.now().month + 2, day=1, hour=0, minute=0,
                                                   second=0, microsecond=0)
        this_month = self.env['vtt.maintenance.plan'].search([
            ('state', '=', 'run'),
            ('equipment_id', '!=', False),
            ('dt_plan', '>=', month_start),
            ('dt_plan', '<', month_next)
        ])
        next_month = self.env['vtt.maintenance.plan'].search([
            ('state', '=', 'run'),
            ('equipment_id', '!=', False),
            ('dt_plan', '>=', month_next),
            ('dt_plan', '<', month_stop)
        ])
        this_month_partners = this_month.mapped('equipment_id')
        next_month_partners = next_month.mapped('equipment_id')
        for e in self:
            e.maintenance_plan_this_month = e in this_month_partners
            e.maintenance_plan_next_month = e in next_month_partners

    @api.model
    def _search_value_maintenance_plan_this_month(self, operator, value):
        recs = self.search([]).filtered(lambda p: p.maintenance_plan_this_month is True)

        return [('id', 'in', [x.id for x in recs])]

    @api.model
    def _search_value_maintenance_plan_next_month(self, operator, value):
        recs = self.search([]).filtered(lambda p: p.maintenance_plan_next_month is True)

        return [('id', 'in', [x.id for x in recs])]

    def _get_warranty(self):
        WarrantyTicket = self.env['vtt.warranty.ticket']
        for e in self:
            e_warranty = WarrantyTicket.search([
                ('equipment_id', '=', e.id),
                ('type', '=', 'general'),
                ('state', 'in', ('1_valid', '2_expire'))
            ], limit=1, order='state, date_warranty desc')
            if e_warranty:
                e.date_warranty = e_warranty.date_warranty
            else:
                e.date_warranty = False

    def _get_valid_warranty(self):
        return self.env['vtt.warranty.ticket'].search([
            ('equipment_id', 'in', self.ids),
            ('type', '=', 'general'),
            ('state', 'in', ['1_valid'])
        ])

    def _expire_all_warranty(self):
        warranties = self._get_valid_warranty()
        warranties.action_expire()

    def _expire_old_warranty(self):
        warranties = self._get_valid_warranty()
        old_warranties = warranties.filtered(lambda w: w.date_warranty < fields.Date.today())
        old_warranties.action_expire()

    def _set_warranty(self):
        warranty_vals = []
        for e in self:
            if e.date_warranty:
                dt = fields.Date.context_today(e)
                data = {'equipment_id': e.id, 'partner_id': e.partner_id.id, 'type': 'general', 'date_warranty': e.date_warranty}
                warranty_vals.append(data)
                e._expire_all_warranty()
        if warranty_vals:
            new_warranty = self.env['vtt.warranty.ticket'].create(warranty_vals)
            # Old fashion
            warranty_to_valid = new_warranty.filtered(lambda w: w.date_warranty >= fields.Date.today())
            warranty_to_valid.action_valid()
            warranty_to_expire = new_warranty - warranty_to_valid
            warranty_to_expire.action_expire()

    @api.depends('repair_order_ids')
    def _compute_repair_order_count(self):
        for e in self:
            e.repair_order_count = len(e.repair_order_ids)

    def action_view_repair(self):
        action = self.env["ir.actions.actions"]._for_xml_id("vtt_mro.vtt_act_window_repair_order")
        repairs = self.repair_order_ids

        if len(repairs) > 1:
            action['domain'] = [('id', 'in', repairs.ids)]
        elif repairs:
            form_view = [(False, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = repairs.id
        # Prepare the context.
        action['context'] = dict(
            self._context,
            default_partner_id=self.partner_id.id,
            default_equipment_id=self.id,)
        return action

    def action_view_maintenance(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('vtt_mro.vtt_act_window_maintenance_plan')
        action['domain'] = [('equipment_id', '=', self.id)]
        context = {
            'default_partner_id': self.partner_id.id,
            'default_equipment_id': self.id,
        }
        action['context'] = context
        return action

    def action_view_warranty(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('vtt_mro.vtt_act_window_warranty_ticket')
        action['domain'] = [('equipment_id', '=', self.id)]
        context = {
            'default_partner_id': self.partner_id.id,
            'default_equipment_id': self.id,
        }
        action['context'] = context
        return action