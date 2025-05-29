# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_template_id = fields.Many2one('vtt.project.template', 'Project Template')
    vtt_project_id = fields.Many2one('project.project', 'Sale Project')

    @api.onchange('sale_order_template_id')
    def onchange_order_template_id(self):
        if self.sale_order_template_id:
            self.project_template_id = self.sale_order_template_id.project_template_id.id

    def start_project_from_template(self):
        self.ensure_one()
        if self.project_template_id and self.state == 'sale':
            new_project = self.project_template_id.project_from_template(partner_id=self.partner_id, sale_id=self)
            self.vtt_project_id = new_project
            return new_project
        return

    def action_open_sale_project(self):
        action = self.env["ir.actions.actions"]._for_xml_id("project.act_project_project_2_project_task_all")
        action['domain'] = [('project_id', '=', self.vtt_project_id.id), ('display_in_project', '=', True)]
        action['context'] = {
            'default_project_id': self.vtt_project_id.id,
            'show_project_update': True,
            'search_default_open_tasks': 1,
        }
        return action