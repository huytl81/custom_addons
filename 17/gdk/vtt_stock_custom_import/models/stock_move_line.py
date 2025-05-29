# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
# from datetime import datetime, timedelta
# from more_itertools import chunked, divide


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    _order = "sequence, result_package_id desc, location_id asc, location_dest_id asc, picking_id, id"

    sequence = fields.Integer('Sequence', default=1)