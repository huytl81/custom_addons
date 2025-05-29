# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CarRepairSupport(models.Model):
    _inherit = 'car.repair.support'

    project_id = fields.Many2one(default=lambda self: self.env.ref('vtt_mro_expand.vtt_mro_repair_project'))

    def create_car_diagnosys(self):
        task_vals = {
            'default_name': self.name,
            'default_user_id': self.user_id.id,
            'default_date_deadline': self.close_date,
            'default_project_id': self.project_id.id,
            'default_partner_id': self.partner_id.id,
            # 'default_description': self.description,
            'default_car_ticket_id': self.id,
            'default_car_task_type': 'diagnosys',
        }
        action = self.env.ref('car_repair_maintenance_service.action_view_task_diagnosis_car')
        result = action.read()[0]
        result['context'] = task_vals
        result['views'] = [(False, 'form')]
        return result

    def create_work_order(self):
        task_vals = {
            'default_name': self.name,
            'default_user_id': self.user_id.id,
            'default_date_deadline': self.close_date,
            'default_project_id': self.project_id.id,
            'default_partner_id': self.partner_id.id,
            'default_description': self.description,
            'default_car_ticket_id': self.id,
            'default_car_task_type': 'work_order',
        }
        action = self.env.ref('car_repair_maintenance_service.action_view_task_workorder')
        result = action.read()[0]
        result['context'] = task_vals
        result['views'] = [(False, 'form')]
        return result

    support_type_id = fields.Many2one('vtt.car.repair.support.type', 'Support Type')

    # Customer rating
    rate_communication_select = fields.Selection([
        ('0', 'None'),
        ('1', 'Poor'),
        ('2', 'Average'),
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent')
    ], 'Communication Skill', default='3')
    rate_standard_select = fields.Selection([
        ('0', 'None'),
        ('1', 'Poor'),
        ('2', 'Average'),
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent')
    ], 'Standard Level', default='3')
    rate_time_select = fields.Selection([
        ('0', 'None'),
        ('1', 'Poor'),
        ('2', 'Average'),
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent')
    ], 'Response Time', default='3')
    rate_orderly_select = fields.Selection([
        ('0', 'None'),
        ('1', 'Poor'),
        ('2', 'Average'),
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent')
    ], 'Safety and Orderly', default='3')
    rate_price_select = fields.Selection([
        ('0', 'None'),
        ('1', 'Poor'),
        ('2', 'Average'),
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent')
    ], 'Price Feel', default='3')

    # Rating value
    rate_communication_value = fields.Float('Communication Skill', group_operator='avg', compute='_get_rating_value', store=True)
    rate_standard_value = fields.Float('Standard Level', group_operator='avg', compute='_get_rating_value', store=True)
    rate_time_value = fields.Float('Response Time', group_operator='avg', compute='_get_rating_value', store=True)
    rate_orderly_value = fields.Float('Safety and Orderly', group_operator='avg', compute='_get_rating_value', store=True)
    rate_price_value = fields.Float('Price Feel', group_operator='avg', compute='_get_rating_value', store=True)
    rate_text_other = fields.Text('Other')

    @api.depends(
        'rate_communication_select',
        'rate_standard_select',
        'rate_time_select',
        'rate_orderly_select',
        'rate_price_select'
    )
    def _get_rating_value(self):
        for t in self:
            t.rate_communication_value = float(t.rate_communication_select)
            t.rate_standard_value = float(t.rate_standard_select)
            t.rate_time_value = float(t.rate_time_select)
            t.rate_orderly_value = float(t.rate_orderly_select)
            t.rate_price_value = float(t.rate_price_select)

    rate_total_select_auto = fields.Selection([
        ('0', 'None'),
        ('1', 'Poor'),
        ('2', 'Average'),
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent')
    ], 'Total Rating', default='3', compute='_compute_total_rating', store=True)
    rate_total_value_auto = fields.Float('Total Rating', group_operator="avg", compute='_compute_total_rating', store=True)

    @api.depends(
        'rate_communication_value',
        'rate_standard_value',
        'rate_time_value',
        'rate_orderly_value',
        'rate_price_value'
    )
    def _compute_total_rating(self):
        for t in self:
            total_rate = (t.rate_communication_value + t.rate_standard_value + t.rate_time_value + t.rate_orderly_value + t.rate_price_value) / 5.00
            int_rate = int(round(total_rate))
            t.rate_total_value_auto = total_rate
            t.rate_total_select_auto = str(int_rate)


class VttRepairSupportType(models.Model):
    _name = 'vtt.car.repair.support.type'
    _description = 'Repair Support Type'
    _order = 'sequence desc,name'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    code = fields.Char('Code')
    sequence = fields.Integer('Priority', default=1)