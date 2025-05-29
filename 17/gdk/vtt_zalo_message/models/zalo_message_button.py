
from odoo import api, fields, models



class ZaloMessageButton(models.Model):
    _name = 'zalo.message.button'
    _description = 'Zalo Message Button'

    name = fields.Char(string='Button Name', required=True)
    action_type = fields.Selection([
        ('oa.open.url', 'Open url'),
        ('oa.query.show', 'Query show'),
        ('oa.query.hide', 'Query hide'),
        ('oa.open.sms', 'Open SMS'),
        ('oa.open.phone', 'Open Phone'),                
    ], string='Action Type', required=True)
    action_value = fields.Char(string='Action Value', required=True)
    template_id = fields.Many2one('zalo.message.template', string='Template', required=True)