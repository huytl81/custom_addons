# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    vtt_material_template_ids = fields.One2many('vtt.product.material.template', 'product_template_id', 'Materials')

    def action_view_material_template(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'vtt.product.material.template',
            'domain': [('product_template_id', '=', self.id)],
            'name': _('Material Templates'),
            'context': {'default_product_template_id': self.id}
        }