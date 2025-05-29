# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VttProductMaterialTemplate(models.Model):
    _name = 'vtt.product.material.template'
    _description = 'Product Materials'

    name = fields.Char('Name', required=True)
    product_template_id = fields.Many2one('product.template', 'Product')

    material_ids = fields.One2many('vtt.product.material.line', 'material_template_id', 'Materials')

    material_count = fields.Integer('Material Count', compute='_compute_material_count')

    duplicate_product = fields.Boolean('Show Duplicate Product', default=False)

    def _compute_material_count(self):
        for m in self:
            m.material_count = len(m.material_ids)

    def action_product_material_wizard(self):
        view_id = self.env.ref('vtt_product_material.vtt_view_tree_product_product_material_choose').id
        domain = []
        if self.duplicate_product:
            domain = [('id', 'not in', self.material_ids.product_id.ids)]

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'product.product',
            'views': [[view_id, "tree"]],
            'name': _('Product Material Wizard'),
            'context': {'material_template_id': self.id},
            'target': 'new',
            'domain': domain,
        }

    @api.model
    def update_material_products(self, material_id, product_ids):
        material = self.browse(material_id)
        material_ids = []
        if material and product_ids:
            for p_id in product_ids:
                product = self.env['product.product'].browse(p_id)
                if product:
                    vals = {
                        'product_id': p_id,
                        'uom_id': product.uom_id.id,
                        'uom_qty': 1.0,
                    }
                    material_ids.append((0, 0, vals))

            if material_ids:
                material.write({
                    'material_ids': material_ids
                })


class VttProductMaterialLine(models.Model):
    _name = 'vtt.product.material.line'
    _description = 'Product Material Line'

    material_template_id = fields.Many2one('vtt.product.material.template', 'Template')

    product_id = fields.Many2one('product.product', 'Product')
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure')
    uom_qty = fields.Float('Quantity', digits='Stock Weight', default=1.0)

    uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')

    def name_get(self):
        result = []
        for l in self:
            result.append((l.id, l.product_id and l.product_id.name or ''))

        return result

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id
            self.uom_qty = 1.0