
from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = "res.users"

    enable_chatter_button = fields.Boolean("Enable Chatter", help="If this checkbox field is checked then the user will be shown hide and show icon", default=True)

    @api.model
    def get_chatter_toggle_flag(self, user_id=None):
        user = self.browse(user_id or self.env.user.id)
        
        # Check if the user is an admin (group ID: `base.group_system`)
        is_admin = user.has_group('base.group_system')

        
        enable_chatter_button = int(user.enable_chatter_button)

        return {
            "user_id": user.id,
            "enable_chatter_button": enable_chatter_button
        }
