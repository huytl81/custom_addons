# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class RepairDiagnosis(models.Model):
    _name = 'vtt.repair.diagnosis'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Repair Diagnosis'
    _order = 'dt_diagnosis desc, partner_id, equipment_id, dt_approve desc'

    name = fields.Char('Name', default=lambda self: _('New'))
    repair_order_id = fields.Many2one('vtt.repair.order', 'Repair Order', tracking=1)
    partner_id = fields.Many2one('res.partner', 'Partner', related='repair_order_id.partner_id', store=True, tracking=2)

    phone = fields.Char('Phone', related='repair_order_id.partner_id.phone')
    email = fields.Char('Email', related='repair_order_id.partner_id.email')

    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user, tracking=4)

    dt_diagnosis = fields.Datetime('Diagnosis Date', default=fields.Datetime.now)
    dt_approve = fields.Datetime('Approve Date')

    equipment_id = fields.Many2one('vtt.equipment.equipment', 'Equipment', related='repair_order_id.equipment_id', store=True, tracking=2)
    equipment_model_name = fields.Char('Model', related='repair_order_id.equipment_id.model_name')
    equipment_manufacture = fields.Char('Manufacture', related='repair_order_id.equipment_id.manufacture')
    equipment_manufacture_year = fields.Char('Year', related='repair_order_id.equipment_id.manufacture_year')
    equipment_serial_number = fields.Char('Serial Number', related='repair_order_id.equipment_id.serial_number')
    equipment_date_warranty = fields.Date('Warranty', related='repair_order_id.equipment_date_warranty')

    priority = fields.Selection(related='repair_order_id.priority')

    description = fields.Text('Description')
    technical_note = fields.Text('Technical Note')

    diagnosis_line_ids = fields.One2many('vtt.repair.diagnosis.line', 'diagnosis_id', 'Estimation')

    state = fields.Selection([
        ('new', 'New'),
        ('submit', 'Submitted'),
        ('approve', 'Approved'),
        ('cancel', 'Canceled')
    ], 'Status', default='new', tracking=3)

    # sale_order_id = fields.Many2one('sale.order', 'Sale Order')

    @api.onchange('equipment_id')
    def onchange_equipment_id(self):
        if self.equipment_id:
            self.equipment_date_warranty = self.equipment_id.date_warranty

    def action_submit(self):
        return self.write({
            'state': 'submit',
        })

    def _apply_diagnosis(self):
        order = self.repair_order_id
        if order.state not in ('cancel', 'done'):
            order_lines = order.mapped('line_ids')
            sequence = order_lines and max(order_lines.mapped('sequence')) + 1 or False
            order_diags = order_lines.mapped('diagnosis_line_id')
            diags = self.mapped('diagnosis_line_ids')
            diag_2_create = diags - order_diags
            line_2_create = [(0, 0, l._prepare_order_values(sequence)) for l in diag_2_create]

            if line_2_create:
                order.write({'line_ids': line_2_create})

    def action_approve(self):
        self._apply_diagnosis()

        return self.write({
            'state': 'approve',
            'dt_approve': fields.Datetime.now(),
        })

    def action_cancel(self):
        return self.write({
            'state': 'cancel',
            'dt_submit': False,
        })

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("New")) == _("New"):
                seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(vals['dt_diagnosis'])
                ) if 'dt_diagnosis' in vals else None
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'repair.diagnosis', sequence_date=seq_date) or _("New")

        return super().create(vals_list)