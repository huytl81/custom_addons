# -*- coding: utf-8 -*-
from odoo import models


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super().session_info()
        result["contextmenu_enabled"] = self.env.user.contextmenu_enabled
        return result
