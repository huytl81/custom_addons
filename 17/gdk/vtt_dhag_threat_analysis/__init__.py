# -*- coding: utf-8 -*-

from . import models
from . import wizard
from . import reports
from . import controllers

MODELS_SUPPORTED = [
    # 'res.partner', 'res.users',
    'res.partner.category', 'res.partner.title', 'res.partner.industry',
    'res.country', 'res.country.state', 'res.country.group',
    'project.project', 'project.project.stage', 'project.task.type'
]
MODELS_MAIN = [
    'investigate.location', 'investigate.campaign', 'investigate.investigate', 'investigate.department.suggest',
    'threat.malware', 'threat.malware.activity', 'threat.malware.activity.detail', 'threat.malware.activity.type',
    'threat.malware.property', 'threat.malware.subject', 'threat.subject.field.mapper', 'investigate.malware',
    'threat.comparison', 'threat.comparison.field', 'threat.comparison.template', 'threat.comparison.report',
    'threat.comparison.template.field',
]
FIELDS_EXCLUDE = ['create_date', 'create_uid', 'write_uid', 'write_date',
                  'image_128', 'image_256', 'activity_ids', 'channel_ids', 'starred_message_ids',
                  'meeting_ids', 'rating_ids', 'message_ids', 'website_message_ids']


def create_default_audit_rule(env):
    data = []
    for m in MODELS_MAIN:
        model = env[m].sudo()
        m_fields = model.field_id.search([('store', '!=', False), ('name', 'not in', FIELDS_EXCLUDE)])
        m_data = {
            'model_id': model.id,
            'name': model.name,
            'fields_to_exclude_ids': m_fields.ids,
        }
        data.append(m_data)
    new_rules = env['auditlog.rule'].create(data)
    new_rules.subscribe()