# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    #for mobile
    vtt_mobile_image = fields.Binary('Icon on mobile')
    vtt_show_on_mobile = fields.Boolean('Show on mobile', default=False)
    vtt_mobile_order = fields.Integer('Mobile order')