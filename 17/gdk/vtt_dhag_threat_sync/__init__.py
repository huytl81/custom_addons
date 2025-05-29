# -*- coding: utf-8 -*-

from . import models
from . import wizards

MODELS_SUPPORTED = [
    # 'res.partner', 'res.users',
    'res.partner.category', 'res.partner.title', 'res.partner.industry',
    'res.country', 'res.country.state', 'res.country.group',
    'project.project', 'project.project.stage', 'project.task.type'
]


def create_default_s_id_sync_data(env):
    datas = env['ir.model.data'].sudo()

    for m in MODELS_SUPPORTED:
        m_datas = datas.search([('model', '=', m)])
        if m_datas:
            m_model = env[m].sudo()
            for r in m_datas:
                record = m_model.browse(r.res_id)
                record.s_id = record.id