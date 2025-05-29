from odoo import api, fields, models

class ResUser(models.Model):
    _inherit = "res.users"

    is_zalo_account = fields.Boolean(default=False)
    token_ids = fields.One2many("vtt.api.access.token", "user_id", string="Access Tokens")
