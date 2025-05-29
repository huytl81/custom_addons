# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    def _get_default_task_types(self):
        xml_ids = [
            'vtt_myanh_config.vtt_data_project_task_type_new',
            'vtt_myanh_config.vtt_data_project_task_type_progress',
            'vtt_myanh_config.vtt_data_project_task_type_done',
            'vtt_myanh_config.vtt_data_project_task_type_cancel',
        ]
        default_type_ids = self.env['project.task.type']
        for t in xml_ids:
            default_type_ids |= self.env.ref(t, raise_if_not_found=False)
        return default_type_ids.ids

    project_type_id = fields.Many2one('vtt.project.type', 'Project Type')

    project_balance = fields.Monetary(related='analytic_account_id.balance')

    def action_view_tasks_hierarchy_general(self):
        """ return the action to see the tasks analysis report of the project """
        action = self.env['ir.actions.act_window']._for_xml_id('vtt_myanh_config.vtt_act_window_project_task_hierarchy')
        # action['display_name'] = _("%(name)s's Tasks Analysis", name=self.name)
        # action_context = ast.literal_eval(action['context']) if action['context'] else {}
        action_context = {}
        action_context['search_default_project_id'] = self.id
        return dict(action, context=action_context)

    @api.model_create_multi
    def create(self, vals_list):
        # base_account_plan = self.env.ref('analytic.analytic_plan_projects')
        res = super(ProjectProject, self).create(vals_list)
        for p in res:
            if not p.type_ids:
                p.type_ids = p._get_default_task_types()
        return res

    def create_analytic_account(self):
        self.ensure_one()
        default_account_plan = self.env.ref('analytic.analytic_plan_projects')
        action = self.env['ir.actions.actions']._for_xml_id('analytic.action_account_analytic_account_form')
        action['res_id'] = 0
        action['view_mode'] = 'form'
        action['views'] = [(False, 'form')]
        action['context'] = {
            'default_plan_id': default_account_plan.id,
            'default_name': self.name,
            'default_partner_id': self.partner_id.id
        }
        return action

    def view_analytic_account(self):
        # self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('analytic.action_account_analytic_account_form')
        action['res_id'] = self.analytic_account_id.id
        action['view_mode'] = 'form'
        action['views'] = [(False, 'form')]
        return action