# -*- coding: utf-8 -*-

from odoo import models, fields, api


class WarrantyUpdateWizard(models.TransientModel):
    _name = 'vtt.warranty.update.wz'
    _description = 'Warranty Update Wizard'

    equipment_id = fields.Many2one('vtt.equipment.equipment', 'Equipment')
    partner_id = fields.Many2one('res.partner', 'Partner')
    plan_type_id = fields.Many2one('vtt.maintenance.plan.type', 'Plan Type')

    type = fields.Selection([
        ('general', 'General'),
        ('parts', 'Parts'),
    ], 'Type', default='general')
    product_id = fields.Many2one('product.product', 'Related Part')

    date_warranty = fields.Date('Warranty')

    @api.onchange('equipment_id')
    def onchange_equipment_id(self):
        if self.equipment_id:
            self.partner_id = self.equipment_id.partner_id.id
            self.date_warranty = self.equipment_id.date_warranty

    @api.onchange('plan_type_id')
    def onchange_plan_type_id(self):
        if self.plan_type_id:
            dt = fields.Date.today()
            dt_next = self.plan_type_id.get_next_by_period(dt)
            self.date_warranty = dt_next

    def apply_warranty(self):
        warranty_vals = {
            'partner_id': self.partner_id.id,
            'equipment_id': self.equipment_id.id,
            'type': self.type,
            'date_warranty': self.date_warranty
        }
        if self.type == 'parts':
            warranty_vals['product_id'] = self.product_id.id

        # if self.type == 'general':
        #     self.equipment_id._expire_all_warranty()

        new_warranty = self.env['vtt.warranty.ticket'].create(warranty_vals)
        new_warranty.action_valid()

        return True