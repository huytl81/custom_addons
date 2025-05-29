from odoo import fields, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    feed_brand_id = fields.Many2one(
        comodel_name='product.data.feed.brand',
        string='Brand',
    )

