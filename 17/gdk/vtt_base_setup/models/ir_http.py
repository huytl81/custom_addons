# -*- coding: utf-8 -*-

from odoo import models, fields, api


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        res = super(IrHttp, self).session_info()
        brand_title = self.env.company.brand_title or 'Victo'
        res['brand_title'] = brand_title
        return res
