# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = "res.users"

    contextmenu_enabled = fields.Boolean(default=False, string="Context Menu")

    @api.model
    def switch_contextmenu_enabled(self, val):
        self.env.user.sudo().contextmenu_enabled = val
        return self.env.user.contextmenu_enabled
