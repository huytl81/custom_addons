# coding: utf-8

from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    land_plot_id = fields.Many2one('vtt.land.plot', 'Plot')
    is_land_product = fields.Boolean('Is Land Product')

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['land_plot_id'] = ", l.land_plot_id as land_plot_id, t.is_land as is_land_product"
        groupby += ', l.land_plot_id, t.is_land'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
