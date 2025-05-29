# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ThreatSyncRequest(models.Model):
    _name = 'threat.sync.request'
    _description = 'Threat Synchronize Request'
    _order = 'dt desc'

    sync_config_id = fields.Many2one('threat.sync.config', 'Server')
    dt = fields.Datetime('Date')
    state = fields.Selection([
        ('success', 'Success'),
        ('failed', 'Failed'),
    ], 'State')

    upload_content = fields.Text('Upload Result')
    download_content = fields.Text('Download Result')
    fail_content = fields.Text('Failed Detail')

    total_upload = fields.Integer('Total Upload')
    total_download = fields.Integer('Total Download')