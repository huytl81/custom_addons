# coding: utf-8 -*-

from odoo import models, fields, api, _
from . import analysis_tools


class ThreatSyncMixin(models.AbstractModel):
    _name = 'threat.sync.mixin'
    _description = 'Threat Sync Mixin'

    def get_sync_fields_data(self):
        FIELDS = self.env['ir.model.fields']
        mail_mixin_fields = FIELDS.search([('model_id.model', 'in', ['mail.thread', 'mail.activity.mixin'])])
        basic_fields_name = ['id', '__last_update', 'create_date', 'create_uid', 'write_date', 'write_uid', 'display_name']
        ex_fields_name = [f.name for f in mail_mixin_fields]
        ex_fields_name += basic_fields_name

        sync_fields = FIELDS.search([('model_id.model', '=', self._name),
                                     ('name', 'not in', ex_fields_name),
                                     ('readonly', '=', False),
                                     ('ttype', 'not in', ['one2many'])])
        sync_fields_name_regular = [f.name for f in sync_fields if f.ttype not in ['many2one', 'many2many', 'binary']]
        sync_fields_name_many2one = [(f.name, f.relation) for f in sync_fields if f.ttype == 'many2one' and f.relation not in ['res.users', 'investigate.department.suggest', 'ir.model.fields', 'res.partner', 'res.country', 'res.country.state']]
        sync_fields_name_many2many = [(f.name, f.relation) for f in sync_fields if f.ttype == 'many2many' and f.relation not in ['res.users', 'investigate.department.suggest', 'ir.model.fields', 'res.partner', 'res.country', 'res.country.state']]
        sync_fields_name_user_many2one = [f.name for f in sync_fields if f.ttype == 'many2one' and f.relation == 'res.users']
        sync_fields_name_user_many2many = [f.name for f in sync_fields if f.ttype == 'many2many' and f.relation == 'res.users']
        sync_fields_name_department_suggest = [f.name for f in sync_fields if f.ttype == 'many2one' and f.relation == 'investigate.department.suggest']
        sync_fields_name_field_many2one = [f.name for f in sync_fields if f.ttype == 'many2one' and f.relation == 'ir.model.fields']
        sync_fields_name_country = [f.name for f in sync_fields if f.ttype == 'many2one' and f.relation == 'res.country']
        sync_fields_name_country_state = [f.name for f in sync_fields if f.ttype == 'many2one' and f.relation == 'res.country.state']
        sync_fields_data = {
            'regular': sync_fields_name_regular,
            'regular_many2one': sync_fields_name_many2one,
            'regular_many2many': sync_fields_name_many2many,
            'user_many2one': sync_fields_name_user_many2one,
            'user_many2many': sync_fields_name_user_many2many,
            'department_suggest': sync_fields_name_department_suggest,
            'fields': sync_fields_name_field_many2one,
            'country': sync_fields_name_country,
            'country_state': sync_fields_name_country_state
        }
        return sync_fields_data

    def _prepare_push_data(self, dt, sequence_number, type='push'):
        if dt:
            domain = [('write_date', '>', dt)]
        else:
            domain = []
        sync_datas = self.search(domain)
        if type == 'push':
            cr_datas = sync_datas.filtered(lambda m: not m.ss_code)
            wr_datas = sync_datas - cr_datas
        else:
            cr_datas = []
            wr_datas = sync_datas
            sequence_lst = []
        cr_datas_json = []
        wr_datas_json = []
        code_prefix = analysis_tools.model_sync_code_mapper[f'ss.{self._name}']
        sync_fields_data = self.get_sync_fields_data()
        if cr_datas:
            sequence_lst = [f'{code_prefix}{str(n + 1).zfill(5)}' for n in range(sequence_number, sequence_number + len(cr_datas))]
            for n in range(len(sequence_lst)):
                rd = cr_datas[n]
                rd.write({'ss_code': sequence_lst[n]})
                # regular fields
                d = rd.read(sync_fields_data['regular'])[0]
                # relation fields
                if sync_fields_data['regular_many2one']:
                    fn_tmps = [n[0] for n in sync_fields_data['regular_many2one']]
                    for dfn in fn_tmps:
                        d.update({dfn: rd[dfn]['ss_code']})
                if sync_fields_data['regular_many2many']:
                    fn_tmps = [n[0] for n in sync_fields_data['regular_many2many']]
                    for dfn in fn_tmps:
                        d.update({dfn: [i['ss_code'] for i in rd[dfn]]})
                if sync_fields_data['user_many2one']:
                    for dfn in sync_fields_data['user_many2one']:
                        d.update({dfn: rd[dfn]['login']})
                if sync_fields_data['user_many2many']:
                    for dfn in sync_fields_data['user_many2many']:
                        d.update({dfn: [i['login'] for i in rd[dfn]]})
                if sync_fields_data['department_suggest']:
                    for dfn in sync_fields_data['department_suggest']:
                        d.update({dfn: rd[dfn]['name']})
                # Need check-out the fixed code
                if sync_fields_data['fields']:
                    for dfn in sync_fields_data['fields']:
                        d.update({dfn: {'model': rd.type, 'name': rd[dfn].name}})
                if sync_fields_data['country']:
                    for dfn in sync_fields_data['country']:
                        d.update({dfn: {'name': rd[dfn]['name'], 'code': rd[dfn]['code']} if rd[dfn] else False})
                if sync_fields_data['country_state']:
                    for dfn in sync_fields_data['country_state']:
                        d.update({dfn: {'name': rd[dfn]['name'], 'code': rd[dfn]['code'], 'country_code': rd[dfn]['country_id']['code'], 'country_name': rd[dfn]['country_id']['name']} if rd[dfn] else False})

                cr_datas_json.append(d)
        if wr_datas:
            for rd in wr_datas:
                # regular fields
                d = rd.read(sync_fields_data['regular'])[0]
                # relation fields
                if sync_fields_data['regular_many2one']:
                    fn_tmps = [n[0] for n in sync_fields_data['regular_many2one']]
                    for dfn in fn_tmps:
                        d.update({dfn: rd[dfn]['ss_code']})
                if sync_fields_data['regular_many2many']:
                    fn_tmps = [n[0] for n in sync_fields_data['regular_many2many']]
                    for dfn in fn_tmps:
                        d.update({dfn: [i['ss_code'] for i in rd[dfn]]})
                if sync_fields_data['user_many2one']:
                    for dfn in sync_fields_data['user_many2one']:
                        d.update({dfn: rd[dfn]['login']})
                if sync_fields_data['user_many2many']:
                    for dfn in sync_fields_data['user_many2many']:
                        d.update({dfn: [i['login'] for i in rd[dfn]]})
                if sync_fields_data['department_suggest']:
                    for dfn in sync_fields_data['department_suggest']:
                        d.update({dfn: rd[dfn]['name']})
                if sync_fields_data['fields']:
                    for dfn in sync_fields_data['fields']:
                        d.update({dfn: {'model': rd.type, 'name': rd[dfn].name}})
                if sync_fields_data['country']:
                    for dfn in sync_fields_data['country']:
                        d.update({dfn: {'name': rd[dfn]['name'], 'code': rd[dfn]['code']} if rd[dfn] else False})
                if sync_fields_data['country_state']:
                    for dfn in sync_fields_data['country_state']:
                        d.update({dfn: {'name': rd[dfn]['name'], 'code': rd[dfn]['code'], 'country_code': rd[dfn]['country_id']['code'], 'country_name': rd[dfn]['country_id']['name']} if rd[dfn] else False})

                wr_datas_json.append(d)

        return {
            'creates': cr_datas_json,
            'writes': wr_datas_json,
        }

    def extract_sync_data(self, datas, type='push'):
        user = self.env.user
        data_crs = datas.get('creates')
        data_wrs = datas.get('writes')
        if type == 'push':
            cr_datas = data_crs
            wr_datas = data_wrs
        else:
            code_lst = [r['ss_code'] for r in data_wrs]
            owrs = self.search([('ss_code', 'in', code_lst)])
            owrs_code_lst = [r['ss_code'] for r in owrs]
            cr_datas = [r for r in data_wrs if r['ss_code'] not in owrs_code_lst]
            wr_datas = [r for r in data_wrs if r['ss_code'] in owrs_code_lst]
        sync_fields_data = self.get_sync_fields_data()
        if cr_datas:
            crs = []
            for rd in cr_datas:
                if sync_fields_data['regular_many2one']:
                    for dfn in sync_fields_data['regular_many2one']:
                        ex_tmps = self.env[dfn[1]].search([('ss_code', '=', rd[dfn[0]])], limit=1)
                        rd.update({dfn[0]: ex_tmps.id})
                if sync_fields_data['regular_many2many']:
                    for dfn in sync_fields_data['regular_many2many']:
                        ex_tmps = self.env[dfn[1]].search([('ss_code', 'in', rd[dfn[0]])], limit=1)
                        rd.update({dfn[0]: [(5, 0, 0)] + [(4, n.id) for n in ex_tmps]})
                if sync_fields_data['user_many2one']:
                    for dfn in sync_fields_data['user_many2one']:
                        n_user = self.env['res.users'].search([('login', '=', rd[dfn])], limit=1)
                        rd.update({dfn: n_user.id})
                if sync_fields_data['user_many2many']:
                    for dfn in sync_fields_data['user_many2many']:
                        n_users = self.env['res.users'].search([('login', 'in', rd[dfn])])
                        rd.update({dfn: [(5, 0, 0)] + [(4, u.id) for u in n_users]})
                if sync_fields_data['department_suggest']:
                    for dfn in sync_fields_data['department_suggest']:
                        n_department = self.env['investigate.department.suggest'].search([('name', '=', rd[dfn])], limit=1)
                        rd.update({dfn: n_department.id})
                if sync_fields_data['fields']:
                    for dfn in sync_fields_data['fields']:
                        r_field = self.env['ir.model.fields'].search([('model_id.model', '=', rd[dfn]['model']), ('name', '=', rd[dfn]['name'])], limit=1)
                        rd.update({dfn: r_field.id})
                # Country and State
                if sync_fields_data['country']:
                    for dfn in sync_fields_data['country']:
                        if rd[dfn]:
                            country = self.env['res.country'].search([('code', '=', rd[dfn]['code'])], limit=1)
                            if not country:
                                country = self.env['res.country'].create({'name': rd[dfn]['name'], 'code': rd[dfn]['code']})
                            rd.update({dfn: country.id})
                if sync_fields_data['country_state']:
                    for dfn in sync_fields_data['country_state']:
                        if rd[dfn]:
                            country_state = self.env['res.country.state'].search([('code', '=', rd[dfn]['code']), ('country_id.code', '=', rd[dfn]['country_code'])], limit=1)
                            if not country_state:
                                ct = self.env['res.country'].search([('code', '=', rd[dfn]['country_code'])], limit=1)
                                if not ct:
                                    ct = self.env['res.country'].create( {'name': rd[dfn]['country_name'], 'code': rd[dfn]['country_code']})
                                country_state = self.env['res.country.state'].create({'name': rd[dfn]['name'], 'code': rd[dfn]['code'], 'country_id': ct.id})
                            rd.update({dfn: country_state.id})
                crs.append(rd)
            self.create(crs)
        if wr_datas:
            owrs = self.search([('ss_code', 'in', [r['ss_code'] for r in wr_datas])])
            for rd in wr_datas:
                ord = owrs.filtered(lambda r: r.ss_code == rd['ss_code'])
                if sync_fields_data['regular_many2one']:
                    for dfn in sync_fields_data['regular_many2one']:
                        ex_tmps = self.env[dfn[1]].search([('ss_code', '=', rd[dfn[0]])], limit=1)
                        rd.update({dfn[0]: ex_tmps.id})
                if sync_fields_data['regular_many2many']:
                    for dfn in sync_fields_data['regular_many2many']:
                        ex_tmps = self.env[dfn[1]].search([('ss_code', 'in', rd[dfn[0]])], limit=1)
                        rd.update({dfn[0]: [(5, 0, 0)] + [(4, n.id) for n in ex_tmps]})
                if sync_fields_data['user_many2one']:
                    for dfn in sync_fields_data['user_many2one']:
                        n_user = self.env['res.users'].search([('login', '=', rd[dfn])], limit=1)
                        rd.update({dfn: n_user.id})
                if sync_fields_data['user_many2many']:
                    for dfn in sync_fields_data['user_many2many']:
                        n_users = self.env['res.users'].search([('login', 'in', rd[dfn])])
                        rd.update({dfn: [(5, 0, 0)] + [(4, u.id) for u in n_users]})
                if sync_fields_data['department_suggest']:
                    for dfn in sync_fields_data['department_suggest']:
                        n_department = self.env['investigate.department.suggest'].search([('name', '=', rd[dfn])],
                                                                                         limit=1)
                        rd.update({dfn: n_department.id})
                if sync_fields_data['fields']:
                    for dfn in sync_fields_data['fields']:
                        r_field = self.env['ir.model.fields'].search([('model_id.model', '=', rd[dfn]['model']), ('name', '=', rd[dfn]['name'])], limit=1)
                        rd.update({dfn: r_field.id})
                if sync_fields_data['country']:
                    for dfn in sync_fields_data['country']:
                        if rd[dfn]:
                            country = self.env['res.country'].search([('code', '=', rd[dfn]['code'])], limit=1)
                            if not country:
                                country = self.env['res.country'].create({'name': rd[dfn]['name'], 'code': rd[dfn]['code']})
                            rd.update({dfn: country.id})
                if sync_fields_data['country_state']:
                    for dfn in sync_fields_data['country_state']:
                        if rd[dfn]:
                            country_state = self.env['res.country.state'].search([('code', '=', rd[dfn]['code']), ('country_id.code', '=', rd[dfn]['country_code'])], limit=1)
                            if not country_state:
                                ct = self.env['res.country'].search([('code', '=', rd[dfn]['country_code'])], limit=1)
                                if not ct:
                                    ct = self.env['res.country'].create( {'name': rd[dfn]['country_name'], 'code': rd[dfn]['country_code']})
                                country_state = self.env['res.country.state'].create({'name': rd[dfn]['name'], 'code': rd[dfn]['code'], 'country_id': ct.id})
                            rd.update({dfn: country_state.id})
                ord.write(rd)