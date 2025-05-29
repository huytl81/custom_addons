# -*- coding: utf-8 -*-

from odoo import models, fields


class ProjectType(models.Model):
    _name = 'vtt.project.type'
    _description = 'Project Type'

    name = fields.Char('Name')
    project_ids = fields.One2many('project.project', 'project_type_id', 'Projects')