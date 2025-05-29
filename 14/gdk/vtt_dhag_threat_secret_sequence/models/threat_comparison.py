# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ThreatComparison(models.Model):
    _inherit = 'threat.comparison'

    @api.model
    def create(self, vals):
        if not vals.get('ss_code', False):
            vals['ss_code'] = self.env['ir.sequence'].next_by_code('ss.threat.comparison')
        return super(ThreatComparison, self).create(vals)


class ThreatComparisonField(models.Model):
    _inherit = 'threat.comparison.field'

    @api.model
    def create(self, vals):
        if not vals.get('ss_code', False):
            vals['ss_code'] = self.env['ir.sequence'].next_by_code('ss.threat.comparison.field')
        return super(ThreatComparisonField, self).create(vals)


class ThreatComparisonTemplate(models.Model):
    _inherit = 'threat.comparison.template'

    @api.model
    def create(self, vals):
        if not vals.get('ss_code', False):
            vals['ss_code'] = self.env['ir.sequence'].next_by_code('ss.threat.comparison.template')
        return super(ThreatComparisonTemplate, self).create(vals)


class ThreatComparisonTemplateField(models.Model):
    _inherit = 'threat.comparison.template.field'

    @api.model
    def create(self, vals):
        if not vals.get('ss_code', False):
            vals['ss_code'] = self.env['ir.sequence'].next_by_code('ss.threat.comparison.template.field')
        return super(ThreatComparisonTemplateField, self).create(vals)


class ThreatComparisonReport(models.Model):
    _inherit = 'threat.comparison.report'

    @api.model
    def create(self, vals):
        if not vals.get('ss_code', False):
            vals['ss_code'] = self.env['ir.sequence'].next_by_code('ss.threat.comparison.report')
        return super(ThreatComparisonReport, self).create(vals)