# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import get_lang
from hashlib import md5


class WarrantyTicket(models.Model):
    _name = 'vtt.warranty.ticket'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Warranty Ticket'
    _order = 'state, date_warranty desc, partner_id, equipment_id'

    equipment_id = fields.Many2one('vtt.equipment.equipment', 'Equipment', tracking=2)
    equipment_model_name = fields.Char('Model', related='equipment_id.model_name')
    equipment_manufacture = fields.Char('Manufacture', related='equipment_id.manufacture')
    equipment_manufacture_year = fields.Char('Year', related='equipment_id.manufacture_year')
    equipment_serial_number = fields.Char('Serial Number', related='equipment_id.serial_number')

    date_warranty = fields.Date('Warranty', required=True, tracking=5)

    partner_id = fields.Many2one('res.partner', 'Partner', tracking=1)
    phone = fields.Char('Phone', related='partner_id.phone')
    email = fields.Char('Email', related='partner_id.email')

    type = fields.Selection([
        ('general', 'General'),
        ('parts', 'Parts'),
    ], 'Type', default='general', tracking=4)
    product_id = fields.Many2one('product.product', 'Related Part', tracking=4)

    state = fields.Selection([
        ('0_draft', 'Draft'),
        ('1_valid', 'Valid'),
        ('2_expire', 'Expired'),
    ], 'Status', default='0_draft', tracking=3)

    code = fields.Char('Warranty Code', compute='_compute_code', store=True)

    # plan_type_id = fields.Many2one('vtt.maintenance.plan.type', 'Plan Type', required=True)

    @api.depends('partner_id', 'equipment_id', 'date_warranty')
    def _compute_code(self):
        for w in self:
            name = '%s %s - %s' % (w.partner_id.name or '', w.equipment_id.name or '', fields.Date.to_string(w.date_warranty))
            dt = fields.Datetime.now().strftime(get_lang(self.env).date_format)
            code = f'{name} {dt}'
            w.code = md5(code.encode('utf-8')).hexdigest()

    @api.depends('partner_id', 'equipment_id', 'date_warranty')
    def _compute_display_name(self):
        for w in self:
            name = '%s %s - %s' % (w.partner_id.name or '', w.equipment_id.name or '', fields.Date.to_string(w.date_warranty))
            w.display_name = name

    def action_valid(self):
        for w in self:
            if w.type == 'general':
                w_e_valids = w.equipment_id._get_valid_warranty() - w
                w_e_valids.action_expire()

        return self.write({
            'state': '1_valid'
        })

    def action_expire(self):

        return self.write({
            'state': '2_expire'
        })