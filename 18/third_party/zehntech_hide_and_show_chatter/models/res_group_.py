

from odoo import models, fields, api

class ResGroups(models.Model):
    _inherit = 'res.groups'

    enable_chatter_group = fields.Boolean(string="Enable Chatter Group", help="If this checkbox field is checked then the group will be shown hide and show icon", default=False)

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def get_chatter_toggle_group_flag(self):
        user = self.env.user
        enable_chatter_group = any(user.groups_id.filtered(lambda group: group.enable_chatter_group))
        return {
            "user_id": user.id,
            "enable_chatter_group": 1 if enable_chatter_group else 0
        }
