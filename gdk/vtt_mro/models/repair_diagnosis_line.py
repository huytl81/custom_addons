# -*- coding: utf-8 -*-

from odoo import models, fields, api


class RepairDiagnosisLine(models.Model):
    _name = 'vtt.repair.diagnosis.line'
    _description = 'Repair Diagnosis Line'

    name = fields.Char('Description')

    diagnosis_id = fields.Many2one('vtt.repair.diagnosis', 'Diagnosis')
    repair_order_id = fields.Many2one('vtt.repair.order', 'Repair Order', related='diagnosis_id.repair_order_id', store=True)

    equipment_id = fields.Many2one('vtt.equipment.equipment', 'Equipment', related='diagnosis_id.equipment_id', store=True)

    note = fields.Text('Note')

    state = fields.Selection(string='Status', related='diagnosis_id.state', store=True)

    def _prepare_order_values(self, sequence=False):
        self.ensure_one()
        vals = {
            'name': self.name,
            'repair_order_id': self.repair_order_id.id,
            'diagnosis_line_id': self.id,
            'price_unit': 0.0,
        }
        if sequence:
            vals['sequence'] = sequence
        return vals