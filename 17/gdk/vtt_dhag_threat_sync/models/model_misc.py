# -*- coding: utf-8 -*-

from odoo import models, fields, api

MODELS_SUPPORTED = [
    # 'res.partner', 'res.users',
    'res.partner.category', 'res.partner.title', 'res.partner.industry',
    'res.country', 'res.country.state', 'res.country.group',
    'project.project', 'project.project.stage', 'project.task.type'
]


class ResPartnerCategory(models.Model):
    _name = 'res.partner.category'
    _inherit = ['res.partner.category', 'threat.sync.mixin']


class ResPartnerTitle(models.Model):
    _name = 'res.partner.title'
    _inherit = ['res.partner.title', 'threat.sync.mixin']


class ResPartnerIndustry(models.Model):
    _name = 'res.partner.industry'
    _inherit = ['res.partner.industry', 'threat.sync.mixin']


class ResCountry(models.Model):
    _name = 'res.country'
    _inherit = ['res.country', 'threat.sync.mixin']


class ResCountryState(models.Model):
    _name = 'res.country.state'
    _inherit = ['res.country.state', 'threat.sync.mixin']


class ResCountryGroup(models.Model):
    _name = 'res.country.group'
    _inherit = ['res.country.group', 'threat.sync.mixin']


class ProjectProject(models.Model):
    _name = 'project.project'
    _inherit = ['project.project', 'threat.sync.mixin']


class ProjectStage(models.Model):
    _name = 'project.project.stage'
    _inherit = ['project.project.stage', 'threat.sync.mixin']


class ProjectTaskType(models.Model):
    _name = 'project.task.type'
    _inherit = ['project.task.type', 'threat.sync.mixin']