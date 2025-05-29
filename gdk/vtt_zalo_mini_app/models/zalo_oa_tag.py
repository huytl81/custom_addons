from odoo import api, fields, models

# model chỉ load tag từ zalo
class VttZaloOATag(models.Model):
    _name = "vtt.zalo.oa.tag"

    name = fields.Char(string='Tag name')
    # public_url = fields.Char(string='Public url')
