# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api, _


class EqScanFile(models.TransientModel):
    _name = 'vtt.dispatch.request.reject'
    _description = "Eq Dispatch Request Reject"

    reject_reason = fields.Text('Reason')

    def action_reject(self):
        request = self.env['vtt.official.dispatch.request'].browse(self.env.context.get('active_ids'))
        request.update({'reject_reason':self.reject_reason})
        return request.action_reject()
