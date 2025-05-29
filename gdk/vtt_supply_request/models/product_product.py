# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_domain_locations_new(self, location_ids):
        context = self.env.context
        res = list(super(ProductProduct, self)._get_domain_locations_new(location_ids))
        if context.get('reversed_location', False):
            res[0] = ['!'] + res[0] + [('location_id.usage', '=', 'internal')]
        return tuple(res)