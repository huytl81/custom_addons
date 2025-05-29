# -*- coding:utf8 -*-

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals_list):
        # Set company_id of user's partner company when created
        users = super(ResUsers, self).create(vals_list)
        for user in users:
            # if partner is global we keep it that way
            if not user.partner_id.company_id:
                user.partner_id.company_id = user.company_id
        return users

    def write(self, values):
        # Update user's partner company
        res = super(ResUsers, self).write(values)
        if 'company_id' in values:
            for user in self:
                # if partner is global we keep it that way
                if not user.partner_id.company_id:
                    user.partner_id.write({'company_id': user.company_id.id})
        return res
