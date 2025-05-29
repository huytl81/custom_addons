# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv.expression import get_unaccent_wrapper
import re


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        self = self.with_user(name_get_uid or self.env.uid)
        # as the implementation is in SQL, we force the recompute of fields if necessary
        self.recompute(['display_name'])
        self.flush()
        if args is None:
            args = []
        order_by_rank = self.env.context.get('res_partner_search_mode')
        if (name or order_by_rank) and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            self.check_access_rights('read')
            where_query = self._where_calc(args)
            self._apply_ir_rules(where_query, 'read')
            from_clause, where_clause, where_clause_params = where_query.get_sql()
            from_str = from_clause if from_clause else 'res_partner'
            where_str = where_clause and (" WHERE %s AND " % where_clause) or ' WHERE '

            # search on the name of the contacts and of its company
            search_name = name
            if operator in ('ilike', 'like'):
                search_name = '%%%s%%' % name
            if operator in ('=ilike', '=like'):
                operator = operator[1:]

            unaccent = get_unaccent_wrapper(self.env.cr)

            where_condition_str = ''
            params = self.env['ir.config_parameter'].sudo()
            search_fields_param = params.get_param('vtt_partner_name_search.vtt_contact_name_search_fields', default='')
            search_fields_lst = search_fields_param.split(',')
            valid_fields_lst = []
            if search_fields_lst:
                ir_fields = self.env['ir.model.fields'].search([
                    ('ttype', 'in', ['char', 'text', 'selection']),
                    ('model_id.model', '=', 'res.partner')
                ])
                ir_fields_lst = [f.name for f in ir_fields]

                valid_fields_lst = [n for n in search_fields_lst if n in ir_fields_lst]
                if valid_fields_lst:
                    for f in valid_fields_lst:
                        where_condition_str = where_condition_str + f" OR res_partner.{f} {operator} {unaccent('%s')}"

            fields = self._get_name_search_order_by_fields()

            query = """SELECT res_partner.id
                             FROM {from_str}
                          {where} ({display_name} {operator} {percent}{where_condition})
                         ORDER BY {fields} {display_name} {operator} {percent} desc,
                                  {display_name}
                        """.format(from_str=from_str,
                                   fields=fields,
                                   where=where_str,
                                   operator=operator,
                                   display_name=unaccent('res_partner.display_name'),
                                   where_condition=where_condition_str,
                                   percent=unaccent('%s'), )

            where_clause_params += [search_name] # for display_name
            if valid_fields_lst:
                for f in valid_fields_lst:
                    if f == 'vat':
                        where_clause_params += [re.sub('[^a-zA-Z0-9\-\.]+', '', search_name) or None]
                    else:
                        where_clause_params += [search_name]
            where_clause_params += [search_name]  # for order by
            if limit:
                query += ' limit %s'
                where_clause_params.append(limit)
            self.env.cr.execute(query, where_clause_params)
            return [row[0] for row in self.env.cr.fetchall()]

        return super(ResPartner, self)._name_search(name, args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    def name_get(self):
        res = []
        params = self.env['ir.config_parameter'].sudo()
        get_fields_param = params.get_param('vtt_partner_name_search.vtt_contact_name_get_fields', default='')
        get_fields_lst = get_fields_param.split(',')
        valid_fields_lst = []
        if get_fields_lst:
            ir_fields = self.env['ir.model.fields'].search([
                ('ttype', 'in', ['char', 'text', 'selection']),
                ('model_id.model', '=', 'res.partner')
            ])
            ir_fields_lst = [f.name for f in ir_fields]

            valid_fields_lst = [n for n in get_fields_lst if n in ir_fields_lst]
        for partner in self:
            # name = partner._get_name()
            name = partner.name
            if valid_fields_lst:
                for f in valid_fields_lst:
                    if partner[f]:
                        name = name + ' - ' + partner[f]
            res.append((partner.id, name))
        return res