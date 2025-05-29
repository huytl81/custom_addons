# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG
from lxml import etree
from lxml.builder import E


def name_selection_groups(ids):
    return 'sel_groups_' + '_'.join(str(it) for it in sorted(ids))


def name_boolean_group(id):
    return 'in_group_' + str(id)


class ResUsers(models.Model):
    _inherit = 'res.users'

    vtt_user_type = fields.Selection([
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('member', 'Member'),
    ], 'Type of User', default='member')

class GroupsView(models.Model):
    _inherit = 'res.groups'

    @api.model
    def _update_user_groups_view(self):
        # remove the language to avoid translations, it will be handled at the view level
        self = self.with_context(lang=None)

        # We have to try-catch this, because at first init the view does not
        # exist but we are already creating some basic groups.
        view = self.env.ref('base.user_groups_view', raise_if_not_found=False)
        if not (view and view._name == 'ir.ui.view'):
            return

        if self._context.get('install_filename') or self._context.get(MODULE_UNINSTALL_FLAG):
            # use a dummy view during install/upgrade/uninstall
            xml = E.field(name="groups_id", position="after")

        else:
            group_no_one = view.env.ref('base.group_no_one')
            group_employee = view.env.ref('base.group_user')
            xml0, xml1, xml2, xml3, xml4 = [], [], [], [], []
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
                    # test_reified_groups, put the user category type in invisible
                    # as it's used in domain of attrs of other fields,
                    # and the normal user category type field node is wrapped in a `groups="base.no_one"`,
                    # and is therefore removed when not in debug mode.
                    xml0.append(E.field(name=field_name, invisible="1", on_change="1"))
                    user_type_field_name = field_name
                    user_type_readonly = f'{user_type_field_name} != {group_employee.id}'
                    attrs['widget'] = 'radio'
                    # Trigger the on_change of this "virtual field"
                    attrs['on_change'] = '1'
                    xml1.append(E.field(name=field_name, **attrs))
                    xml1.append(E.newline())

                elif kind == 'selection':
                    # application name with a selection field
                    field_name = name_selection_groups(gs.ids)
                    attrs['readonly'] = user_type_readonly
                    attrs['on_change'] = '1'
                    if category_name not in xml_by_category:
                        xml_by_category[category_name] = []
                        xml_by_category[category_name].append(E.newline())
                    xml_by_category[category_name].append(E.field(name=field_name, **attrs))
                    xml_by_category[category_name].append(E.newline())
                    # add duplicate invisible field so default values are saved on create
                    if attrs.get('groups') == 'base.group_no_one':
                        xml0.append(E.field(name=field_name, **dict(attrs, invisible="1", groups='!base.group_no_one')))

                else:
                    # application separator with boolean fields
                    app_name = app.name or 'Other'
                    xml4.append(E.separator(string=app_name, **attrs))
                    left_group, right_group = [], []
                    attrs['readonly'] = user_type_readonly
                    # we can't use enumerate, as we sometime skip groups
                    group_count = 0
                    for g in gs:
                        field_name = name_boolean_group(g.id)
                        dest_group = left_group if group_count % 2 == 0 else right_group
                        if g == group_no_one:
                            # make the group_no_one invisible in the form view
                            dest_group.append(E.field(name=field_name, invisible="1", **attrs))
                        else:
                            dest_group.append(E.field(name=field_name, **attrs))
                        # add duplicate invisible field so default values are saved on create
                        xml0.append(E.field(name=field_name, **dict(attrs, invisible="1", groups='!base.group_no_one')))
                        group_count += 1
                    xml4.append(E.group(*left_group))
                    xml4.append(E.group(*right_group))

            xml4.append({'class': "o_label_nowrap"})
            user_type_invisible = f'{user_type_field_name} != {group_employee.id}' if user_type_field_name else None

            for xml_cat in sorted(xml_by_category.keys(), key=lambda it: it[0]):
                master_category_name = xml_cat[1]
                xml3.append(E.group(*(xml_by_category[xml_cat]), string=master_category_name))

            field_name = 'user_group_warning'
            user_group_warning_xml = E.div({
                'class': "alert alert-warning",
                'role': "alert",
                'colspan': "2",
                'invisible': f'not {field_name}',
            })
            user_group_warning_xml.append(E.label({
                'for': field_name,
                'string': "Access Rights Mismatch",
                'class': "text text-warning fw-bold",
            }))
            user_group_warning_xml.append(E.field(name=field_name))
            xml2.append(user_group_warning_xml)

            xml = E.field(
                *(xml0),
                E.group(*(xml1), groups="base.group_no_one"),
                E.group(*(xml2), invisible=user_type_invisible),
                E.group(*(xml3), invisible=user_type_invisible),
                E.group(*(xml4), invisible=user_type_invisible), name="groups_id",
                position="replace")
            xml.addprevious(etree.Comment("GENERATED AUTOMATICALLY BY GROUPS"))

        # serialize and update the view
        xml_content = etree.tostring(xml, pretty_print=True, encoding="unicode")
        if xml_content != view.arch:  # avoid useless xml validation if no change
            new_context = dict(view._context)
            new_context.pop('install_filename', None)  # don't set arch_fs for this computed view
            new_context['lang'] = None
            view.with_context(new_context).write({'arch': xml_content})


# class GroupsView(models.Model):
#     _inherit = 'res.groups'
#
#     def _get_hidden_extra_categories(self):
#         res = super(GroupsView, self)._get_hidden_extra_categories()
#         res.append('base.module_category_administration')
#         return res
#
#     @api.model
#     def get_groups_by_application(self):
#         user = self.env.user
#         categ_base = self.env.ref('base.module_category_administration_administration')
#         g_base = self.env.ref('base.group_system')
#         res = super(GroupsView, self).get_groups_by_application()
#         res_categ_base = [c for c in res if categ_base in c[0]]
#         if res_categ_base and not user.has_group('base.group_system'):
#             res_categ = res_categ_base[0]
#             other_categ = [c for c in res if c != res_categ]
#             new_categ = (res_categ[0], res_categ[1], res_categ[2] - g_base, res_categ[3])
#             other_categ.append(new_categ)
#             return other_categ
#         return res

