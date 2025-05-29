# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    vtt_height = fields.Float('Height (cm)')
    vtt_width = fields.Float('Width (cm)')
    vtt_length = fields.Float('Length (cm)')

    packing_specification = fields.Integer('Packing Specification', default=1)

    vtt_tag_ids = fields.Many2many('vtt.product.tag', string='Tags')

    # lot_sequence_counter = fields.Integer('Sequence Counter', default=0)

    pack_barcode = fields.Char('Packing Barcode')
    product_barcode = fields.Char('Product Barcode')