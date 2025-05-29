# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _prepare_push_data(self):
        users = self.search([])
        return {'users': [{'name': u.name, 'email': u.email, 'login': u.login} for u in users]}

    def extract_sync_data(self, datas, type='push'):
        if datas and datas.get('users'):
            r_logins = [u['login'] for u in datas['users']]
            users = self.search([('login', 'in', r_logins)])
            o_logins = [u.login for u in users]
            crs = [{'name': r['name'], 'login': r['login'], 'email': r['email']} for r in datas['users'] if r['login'] not in o_logins]
            self.create(crs)
