# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VttContactUserWizard(models.TransientModel):
    _name = 'vtt.contact.user.wz'
    _description = 'Contact Salesman Wizard'

    user_id = fields.Many2one('res.users', 'User')

    def _get_default_partner(self):
        return self.env['res.partner'].browse(self.env.context.get('active_ids')) or []

    partner_ids = fields.Many2many('res.partner', string='Partners', default=_get_default_partner)

    is_include_child = fields.Boolean('Include Childs?', default=False)
    is_overwrite = fields.Boolean('Over write?', default=True)

    def update_contact_salesman(self):
        if self.partner_ids:
            if self.is_include_child:
                partners = self.env['res.partner'].search([('id', 'child_of', self.partner_ids.ids)])
            else:
                partners = self.partner_ids
            if not self.is_overwrite:
                lst_id = [p.id for p in self.partner_ids if not p.user_id]
                partners = self.env['res.partner'].browse(lst_id)
            if partners:
                partners.write({
                    'user_id': self.user_id.id if self.user_id else False
                })