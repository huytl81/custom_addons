from odoo import api, fields, models
from odoo.tools.translate import html_translate

# clone from ProductPublicCategory
class ProductZaloCategory(models.Model):
    _name = "product.zalo.category"

    name = fields.Char(required=True, translate=True)
    description = fields.Html('Category Description', sanitize_overridable=True, sanitize_attributes=False,
                                      translate=html_translate, sanitize_form=False)
    sequence = fields.Integer('Zalo app menu order')
    image = fields.Image('Image', store=True)
    product_tmpl_ids = fields.Many2many('product.template', relation='product_zalo_category_product_template_rel')

    # title = fields.Char(string='Title')
    # description = fields.Html('Content')
    # publish_date = fields.Datetime(string='Publish date')
    # author = fields.Char(string='Author')
    # avatar = fields.Image('Avatar', store=True)
