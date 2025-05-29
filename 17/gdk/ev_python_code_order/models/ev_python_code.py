# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class EvExecutePythonCode(models.Model):
    _name = 'ev.python.code'
    _description = "Execute Python Code"
    _order = 'sequence'

    name = fields.Char(string='Script Name', required=True)
    code = fields.Text(string='Python Code', required=True)
    result = fields.Text(string='Result', readonly=True)

    sequence = fields.Integer('Sequence', default=10)
    color = fields.Selection([
        ('red', 'Red'),
        ('yellow', 'Yellow'),
        ('green', 'Green'),
        ('blue', 'Blue'),
    ], 'Color')
    notice = fields.Boolean('Notice?', default=False)

    custom_data = fields.Text('Custom Data Stored')

    active = fields.Boolean('Active', default=True)

    def execute_code(self):
        localdict = {'self': self, 'user_obj': self.env.user, 'result': ''}
        for obj in self:
            try:
                exec(obj.code, localdict)
                if localdict.get('result', False):
                    self.write({'result': localdict['result']})
                else:
                    self.write({'result': ''})
            except Exception as e:
                raise UserError('Python code is not able to run ! message : %s' % e)
        return True

