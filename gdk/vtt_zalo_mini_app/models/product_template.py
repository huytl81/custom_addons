from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    # zalo_menu_order = fields.Integer('Zalo app menu order')
    # show_on_zalo = fields.Boolean('Show on Zalo app', default=False)

    zalo_categ_ids = fields.Many2many(
        string="Zalo Product Category",
        comodel_name='zalo.product.category',
        relation='zalo_product_category_product_template_rel',
        help="Zalo product category",
    )

    zalo_description_sale = fields.Text(
        string="Zalo description",
        help="Description for Zalo mini app",
    )

    # title = fields.Char(string='Title')
    # description = fields.Html('Content')
    # publish_date = fields.Datetime(string='Publish date')
    # author = fields.Char(string='Author')
    # avatar = fields.Image('Avatar', store=True)
