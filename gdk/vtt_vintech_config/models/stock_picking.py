# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    partner_street = fields.Char('Tax ID', related='partner_id.street')
    partner_vat = fields.Char('Street', related='partner_id.vat')
    partner_ref = fields.Char('Partner Ref', related='partner_id.ref')

    vintech_street_note = fields.Char('Vintech Other Street', tracking=True)
    vintech_picking_note = fields.Char('Picking Reference Note')