# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _, tools
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG
from lxml import etree
from lxml.builder import E

_logger = logging.getLogger(__name__)


def name_selection_groups(ids):
    return 'sel_groups_' + '_'.join(str(it) for it in ids)


def name_boolean_group(id):
    return 'in_group_' + str(id)


class GroupsView(models.Model):
    _inherit = 'res.groups'

    def _get_hidden_extra_categories(self):
        res = super(GroupsView, self)._get_hidden_extra_categories()
        categ_params = self.env['ir.config_parameter'].sudo().get_param('vtt_admin_config.hidden_extra_categ')
        if categ_params != '':
            addition = categ_params.split(',')
            res += addition
        return res

    def _vtt_get_hidden_selection_categories(self):
        res = []
        categ_params = self.env['ir.config_parameter'].sudo().get_param('vtt_admin_config.hidden_selection_categ')
        if categ_params != '':
            addition = categ_params.split(',')
            res += addition
        return res

    @api.model
    def _update_user_groups_view(self):
        self = self.with_context(lang=None)
        view = self.env.ref('base.user_groups_view', raise_if_not_found=False)
        if not (view and view.exists() and view._name == 'ir.ui.view'):
            return

        if self._context.get('install_filename') or self._context.get(MODULE_UNINSTALL_FLAG):
            # use a dummy view during install/upgrade/uninstall
            xml = E.field(name="groups_id", position="after")

        else:
            group_no_one = view.env.ref('base.group_no_one')
            group_employee = view.env.ref('base.group_user')
            xml1, xml2, xml3 = [], [], []
            xml_by_category = {}
            xml1.append(E.separator(string='User Type', colspan="2", groups='base.group_no_one'))

            user_type_field_name = ''
            user_type_readonly = str({})
            sorted_tuples = sorted(self.get_groups_by_application(),
                                   key=lambda t: t[0].xml_id != 'base.module_category_user_type')
            for app, kind, gs, category_name in sorted_tuples:  # we process the user type first
                attrs = {}
                # hide groups in categories 'Hidden' and 'Extra' (except for group_no_one)
                if app.xml_id in self._get_hidden_extra_categories():
                    attrs['groups'] = 'base.group_no_one'

                # User type (employee, portal or public) is a separated group. This is the only 'selection'
                # group of res.groups without implied groups (with each other).
                if app.xml_id == 'base.module_category_user_type':
                    # application name with a selection field
                    field_name = name_selection_groups(gs.ids)
                    user_type_field_name = field_name
                    user_type_readonly = str({'readonly': [(user_type_field_name, '!=', group_employee.id)]})
                    attrs['widget'] = 'radio'
                    attrs['groups'] = 'base.group_no_one'
                    xml1.append(E.field(name=field_name, **attrs))
                    xml1.append(E.newline())

                elif kind == 'selection':
                    # application name with a selection field
                    field_name = name_selection_groups(gs.ids)
                    attrs['attrs'] = user_type_readonly
                    if category_name not in xml_by_category:
                        xml_by_category[category_name] = []
                        xml_by_category[category_name].append(E.newline())
                    # Add system group to hidden administrator for other roles
                    if app.xml_id in self._vtt_get_hidden_selection_categories():
                        attrs['groups'] = 'base.group_system'
                    xml_by_category[category_name].append(E.field(name=field_name, **attrs))
                    xml_by_category[category_name].append(E.newline())

                else:
                    # application separator with boolean fields
                    app_name = app.name or 'Other'
                    xml3.append(E.separator(string=app_name, colspan="4", **attrs))
                    attrs['attrs'] = user_type_readonly
                    for g in gs:
                        field_name = name_boolean_group(g.id)
                        if g == group_no_one:
                            # make the group_no_one invisible in the form view
                            xml3.append(E.field(name=field_name, invisible="1", **attrs))
                        else:
                            xml3.append(E.field(name=field_name, **attrs))

            xml3.append({'class': "o_label_nowrap"})
            if user_type_field_name:
                user_type_attrs = {'invisible': [(user_type_field_name, '!=', group_employee.id)]}
            else:
                user_type_attrs = {}

            for xml_cat in sorted(xml_by_category.keys(), key=lambda it: it[0]):
                master_category_name = xml_cat[1]
                xml2.append(E.group(*(xml_by_category[xml_cat]), col="2", string=master_category_name))

            xml = E.field(
                E.group(*(xml1), col="2"),
                E.group(*(xml2), col="2", attrs=str(user_type_attrs)),
                E.group(*(xml3), col="4", attrs=str(user_type_attrs)), name="groups_id", position="replace")
            xml.addprevious(etree.Comment("GENERATED AUTOMATICALLY BY GROUPS"))

        # serialize and update the view
        xml_content = etree.tostring(xml, pretty_print=True, encoding="unicode")
        if xml_content != view.arch:  # avoid useless xml validation if no change
            new_context = dict(view._context)
            new_context.pop('install_filename', None)  # don't set arch_fs for this computed view
            new_context['lang'] = None
            view.with_context(new_context).write({'arch': xml_content})


class Users(models.Model):
    _inherit = 'res.users'

    # _sql_constraints = [
    #     ('username_uniq', 'unique (login)', "Username already exists !"),
    # ]

    vtt_user_type = fields.Selection([
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('member', 'Member'),
    ], 'Type of User', default='member')

    @api.onchange('login')
    def on_change_login(self):
        if self.login and not self.email and tools.single_email_re.match(self.login):
            self.email = self.login

    @api.depends('login')
    def _compute_exist_username(self):
        for u in self:
            check = False
            if u.login:
                count = self.sudo().search_count([
                    ('login', '=', u.login)
                ])
                if not u.id and count > 0:
                    check = True
                if u.id and count > 1:
                    check = True
            u.update({
                'vtt_exist_username': check,
            })

    vtt_exist_username = fields.Boolean('Username Existed', compute='_compute_exist_username')


class Partner(models.Model):
    _inherit = 'res.partner'

    def _vtt_default_user_lang(self):
        default_user_id = self.env['ir.model.data'].xmlid_to_res_id('base.default_user', raise_if_not_found=False)
        return self.env['res.users'].browse(default_user_id).sudo().lang if default_user_id else self.env.user.lang

    def _vtt_default_user_tz(self):
        default_user_id = self.env['ir.model.data'].xmlid_to_res_id('base.default_user', raise_if_not_found=False)
        return self.env['res.users'].browse(default_user_id).sudo().tz if default_user_id else self._context.get('tz')

    lang = fields.Selection(default=_vtt_default_user_lang)
    tz = fields.Selection(default=_vtt_default_user_tz)