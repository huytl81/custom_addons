# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.tools import format_datetime

rec = 0
def autoIncrement():
    global rec
    pStart = 1
    pInterval = 1
    if rec == 0:
        rec = pStart
    else:
        rec += pInterval
    return rec


class MrpStockReport(models.TransientModel):
    _inherit = 'stock.traceability.report'

    def _make_dict_move(self, level, parent_id, move_line, unfoldable=False):
        res = super(MrpStockReport, self)._make_dict_move(level, parent_id, move_line, unfoldable)
        rev_perc = ''
        if move_line.picking_code == 'incoming':
            rev_perc = f'{move_line.vtt_expiration_percentage:.{2}f}%'
        res[0]['rev_perc'] = rev_perc
        return res

    @api.model
    def _final_vals_to_lines(self, final_vals, level):
        lines = []
        for data in final_vals:
            lines.append({
                'id': autoIncrement(),
                'model': data['model'],
                'model_id': data['model_id'],
                'parent_id': data['parent_id'],
                'usage': data.get('usage', False),
                'is_used': data.get('is_used', False),
                'lot_name': data.get('lot_name', False),
                'lot_id': data.get('lot_id', False),
                'reference': data.get('reference_id', False),
                'res_id': data.get('res_id', False),
                'res_model': data.get('res_model', False),
                'columns': [data.get('reference_id', False),
                            data.get('product_id', False),
                            format_datetime(self.env, data.get('date', False), tz=False, dt_format=False),
                            data.get('lot_name', False),
                            data.get('location_source', False),
                            data.get('location_destination', False),
                            data.get('product_qty_uom', 0),
                            data.get('rev_perc', '')],
                'level': level,
                'unfoldable': data['unfoldable'],
            })
        return lines