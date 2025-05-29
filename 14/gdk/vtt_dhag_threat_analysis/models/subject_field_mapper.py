# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ThreatSubjectFieldMapper(models.Model):
    _name = 'threat.subject.field.mapper'
    _description = 'Threat Subject Field Mapper'
    _rec_name = 'src_name'

    src_name = fields.Char('Name')
    code = fields.Char('Code')

    line_ids = fields.One2many('threat.subject.field.mapper.line', 'mapper_id', 'Rules')


class ThreatSubjectFieldMapperLine(models.Model):
    _name = 'threat.subject.field.mapper.line'
    _description = 'Threat Subject Field Mapper Rule'

    mapper_id = fields.Many2one('threat.subject.field.mapper', 'Mapper')
    res_field = fields.Char('Field Name')
    src_tag = fields.Char('Src Tag')
    active = fields.Boolean('Active', default=True)

    # _sql_constraints = [
    #     ('mapper_res_field_unique', 'unique(mapper_id, res_field)',
    #      "The mapper already has this field(s)."),
    # ]