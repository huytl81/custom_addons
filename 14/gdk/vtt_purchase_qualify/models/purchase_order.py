# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    vtt_appraiser_id = fields.Many2one('res.users', 'Appraiser', tracking=100)
    vtt_confirm_uid = fields.Many2one('res.users', 'Confirmation User', tracking=100)

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        if res:
            responsible_method = self.env['ir.config_parameter'].sudo().get_param('vtt_purchase_qualify.po_responsible_method')
            if responsible_method and responsible_method == 'auto':
                for order in self:
                    order.write({
                        'vtt_confirm_uid': self.env.user.id
                    })
        return res

    def button_draft(self):
        res = super(PurchaseOrder, self).button_draft()
        self.write({
            'vtt_confirm_uid': False,
            'vtt_appraiser_id': False
        })
        return res
