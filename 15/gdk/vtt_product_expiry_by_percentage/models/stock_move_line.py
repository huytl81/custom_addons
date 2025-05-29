# -*- coding: utf-8 -*-

import datetime
from odoo import models, fields, api, _


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    vtt_expiration_percentage = fields.Float('% Expiration Time',
                                             compute='_compute_expiration_time_percentage',
                                             store=True)
    vtt_production_date = fields.Date('Production Date', compute='_compute_vtt_production_date', store=True)

    @api.depends('lot_id.vtt_production_date', 'expiration_date')
    def _compute_vtt_production_date(self):
        for move_line in self:
            if move_line.lot_id.vtt_production_date:
                move_line.vtt_production_date = move_line.lot_id.vtt_production_date
            elif move_line.picking_type_use_create_lots:
                if move_line.expiration_date:
                    product_expiration_time = move_line.product_id.expiration_time
                    move_line.vtt_production_date = move_line.expiration_date - datetime.timedelta(days=product_expiration_time)

    # @api.onchange('lot_id')
    # def onchange_lot_vtt_production_date(self):
    #     if self.lot_id:
    #         self.vtt_production_date = self.lot_id.vtt_production_date

    @api.depends('expiration_date', 'vtt_production_date')
    def _compute_expiration_time_percentage(self):
        date = datetime.datetime.now()
        for move_line in self:
            perc = 100
            if move_line.expiration_date:
                if not move_line.product_id.vtt_use_production_date:
                    product_expiration_time = move_line.product_id.expiration_time
                elif move_line.product_id.vtt_use_production_date and move_line.vtt_production_date:
                    production_date = fields.Datetime.to_datetime(move_line.vtt_production_date)
                    product_expiration_time = (move_line.expiration_date - production_date).days
                else:
                    product_expiration_time = (move_line.expiration_date - date).days

                date_diff = (move_line.expiration_date - date).days

                # Old solution
                # if date_diff and product_expiration_time:
                #     date_diff_percentage = date_diff / product_expiration_time * 100
                #     perc = date_diff_percentage

                if product_expiration_time:
                    if date_diff:
                        date_diff_percentage = date_diff / product_expiration_time * 100
                        perc = date_diff_percentage
                    else:
                        perc = 0
                elif product_expiration_time == 0:
                    if date_diff < 0:
                        perc = 0

            move_line.vtt_expiration_percentage = perc

    def _assign_production_lot(self, lot):
        super()._assign_production_lot(lot)
        self.lot_id.vtt_create_expiration_percentage = self[0].vtt_expiration_percentage
        self.lot_id.vtt_production_date = self[0].vtt_production_date
        if self.lot_id.product_id.vtt_use_production_date:
            if self.lot_id.vtt_production_date and self.lot_id.expiration_date:
                production_date = fields.Datetime.to_datetime(self.lot_id.vtt_production_date)
                product_expiration_time = (self.lot_id.expiration_date - production_date).days
                self.lot_id.product_id.expiration_time = product_expiration_time
                self.lot_id.product_id.product_tmpl_id.update_product_expiration_time()