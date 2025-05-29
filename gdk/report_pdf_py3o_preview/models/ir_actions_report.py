# -*- coding: utf-8 -*-

from odoo import models


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _get_readable_fields(self):
        return super()._get_readable_fields() | {"py3o_filetype"}