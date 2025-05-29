from odoo import api, fields, models
from odoo.tools.translate import html_translate

# clone from ProductPublicCategory
class ZaloProductCategory(models.Model):
    _name = "zalo.product.category"

    name = fields.Char(required=True)
    description = fields.Html('Category Description', sanitize_overridable=True, sanitize_attributes=False, sanitize_form=False)
    sequence = fields.Integer('Zalo app menu order')
    image = fields.Image('Image', store=True)
    product_tmpl_ids = fields.Many2many('product.template', relation='zalo_product_category_product_template_rel')

    # title = fields.Char(string='Title')
    # description = fields.Html('Content')
    # publish_date = fields.Datetime(string='Publish date')
    # author = fields.Char(string='Author')
    # avatar = fields.Image('Avatar', store=True)
