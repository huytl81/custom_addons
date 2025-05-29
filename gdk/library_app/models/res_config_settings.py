# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_self_borrow = fields.Boolean(string="Self Borrow", implied_group='library_app.group_self_borrow')
    # group_self_borrow = fields.Boolean(string="Self Borrow", config_parameter='Self Borrow', implied_group='library_app.group_self_borrow')
