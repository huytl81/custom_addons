# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    maintenance_mode = fields.Boolean(string='Maintenance Mode',
                                      config_parameter='hspl.maintenance_mode')

    def onchange_maintenance_mode(self, field_value, module_name):
        if module_name == 'maintenance_mode' and field_value and self.env.context.get('maintenance_mode_check'):
            return {
                'warning': {
                    'title': _('Warning!'),
                    'message': _('Are you sure you wanted to activate the maintenance mode.!'),
                }
            }
        return {}

    def _register_hook(self):
        def make_maintenance_mode(name):
            return lambda self: self.onchange_maintenance_mode(self[name], name)

        for name in self._fields:
            if name.startswith('maintenance_mode'):
                method = make_maintenance_mode(name)
                self._onchange_methods[name].append(method)
