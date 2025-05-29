# -*- coding: utf-8 -*-
# Part of Kiran Infosoft. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    relation_start_date = fields.Date(
        string="Relation Start Date",
    )

    @api.model
    def _run_action_partner_notification(self):
        tmpl = False

        aa = self.env['res.partner'].search([])
        for i in aa:
            print(i.company_id)
            print(i.name)
            print(i.company_id.name)

        try:
            tmpl = self.env.ref(
                'ki_partner_relation_reminder.email_tmpl_partner_anniversary'
            )
        except:
            pass

        current_date = fields.Date.today()
        day = current_date.day
        month = current_date.month

        self._cr.execute("""
            SELECT
                id
            FROM
                res_partner
            WHERE
                extract(month from  relation_start_date) = '%s' AND
                extract(day from  relation_start_date) = '%s'
        """ %(month, day))

        res = self._cr.dictfetchall()
        print("___________")
        partners = [r['id'] for r in res]

        for partner in partners:
            if tmpl:
                tmpl.send_mail(partner)



        # user = self.env.user
        # tmpl = False
        # aa = self.env['res.partner'].search([])
        # for i in aa:
        #     print(i.company_id)
        #     print(i.name)
        #     print(i.company_id.name)
        #
        # try:
        #     tmpl = self.env.ref(
        #         'ki_partner_relation_reminder.email_tmpl_partner_anniversary'
        #     )
        # except:
        #     pass
        #
        # current_date = fields.Date.today()
        # day = current_date.day
        # month = current_date.month
        #
        # self._cr.execute("""
        #     SELECT
        #         id
        #     FROM
        #         res_partner
        #     WHERE
        #         extract(month from  relation_start_date) = '%s' AND
        #         extract(day from  relation_start_date) = '%s'
        # """ %(month, day))
        #
        # res = self._cr.dictfetchall()
        # print("___________")
        # partners = [r['id'] for r in res]

        # for partner in partners:
        #     if tmpl:
        #         ctx = self._context.copy()
        #         tmpl.with_context(ctx).send_mail(partner.id)
