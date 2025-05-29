from odoo import api, fields, models

class ProductCategory(models.Model):
    _inherit = "product.category"

    zalo_menu_order = fields.Integer('Zalo app menu order')
    show_on_zalo = fields.Boolean('Show on Zalo app', default=False)

    # title = fields.Char(string='Title')
    # description = fields.Html('Content')
    # publish_date = fields.Datetime(string='Publish date')
    # author = fields.Char(string='Author')
    # avatar = fields.Image('Avatar', store=True)
