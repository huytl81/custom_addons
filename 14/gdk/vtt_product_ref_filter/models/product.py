# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    vtt_related_product_ids = fields.Many2many('product.product', string='Related Products')

    def write(self, vals):
        current_ids = self.vtt_related_product_ids.ids
        res = super(ProductTemplate, self).write(vals)

        if 'vtt_related_product_ids' in vals and vals.get('vtt_related_product_ids')[0][0] == 6:
            this_product = self.env['product.product'].search([('product_tmpl_id', '=', self.id)])

            change_ids = vals.get('vtt_related_product_ids')[0][2]

            add_products = self.env['product.product'].browse([i for i in change_ids if i not in current_ids])
            remove_products = self.env['product.product'].browse([i for i in current_ids if i not in change_ids])

            if add_products:
                add_products.product_tmpl_id.write({
                    'vtt_related_product_ids': [(4, p.id) for p in this_product]
                })
            if remove_products:
                remove_products.product_tmpl_id.write({
                    'vtt_related_product_ids': [(3, p.id) for p in this_product]
                })

        return res


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        # default_code_context = self._context.get('display_default_code', False)

        res = super(ProductProduct, self).name_search(name, args, operator, limit)

        if res:
            products = self.browse([p[0] for p in res])
            tmpls = products.product_tmpl_id

            addition_ids = self._name_search('', [('product_tmpl_id', 'in', tmpls.vtt_related_product_ids.ids)])
            addition_products = self.browse(addition_ids).sudo().name_get()
            res += addition_products

        return res[:limit]