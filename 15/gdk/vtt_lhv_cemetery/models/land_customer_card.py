# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VttLandCustomerCard(models.Model):
    _name = 'vtt.land.customer.card'
    _description = 'Land Customer Card'

    code = fields.Char('Code')
    partner_id = fields.Many2one('res.partner', 'Partner')
    phone = fields.Char(related='partner_id.phone', store=True)
    mobile = fields.Char(related='partner_id.mobile', store=True)

    dt_assign = fields.Datetime('Assign Date', default=fields.Datetime.now)

    plot_id = fields.Many2one('vtt.land.plot', 'Plot')

    active = fields.Boolean('Active', default=True)

    is_assigned = fields.Boolean('Assigned?', compute='_compute_is_assigned', store=True)

    @api.depends('partner_id', 'plot_id')
    def _compute_is_assigned(self):
        for lcc in self:
            if lcc.partner_id or lcc.plot_id:
                lcc.is_assigned = True
            else:
                lcc.is_assigned = False

    def name_get(self):
        result = []
        for lcc in self:
            name = f'{lcc.code} - {lcc.partner_id.name} - {lcc.partner_id.phone}'
            result.append((lcc.id, name))
        return result

    def action_unassigned(self):
        return self.write({
            'partner_id': False,
            'plot_id': False,
            'dt_assign': False
        })