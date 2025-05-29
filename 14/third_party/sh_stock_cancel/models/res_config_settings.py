# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    picking_operation_type = fields.Selection([('cancel', 'Cancel Only'), ('cancel_draft', 'Cancel and Reset to Draft'), ('cancel_delete', 'Cancel and Delete')],
                                              default='cancel', string="Stock Picking Opration Type")

    adj_operation_type = fields.Selection([('cancel', 'Cancel Only'), ('cancel_draft', 'Cancel and Reset to Draft'), ('cancel_delete', 'Cancel and Delete')],
                                          default='cancel', string="Stock Adjustement Opration Type")

    
    scrap_operation_type = fields.Selection([('cancel','Cancel Only'),('cancel_draft','Cancel and Reset to Draft'),('cancel_delete','Cancel and Delete')],
                                      default='cancel',string="Scrap Opration Type")
    
    
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    picking_operation_type = fields.Selection(default=lambda self: self.env.company.picking_operation_type, string="Stock Picking Opration Type", related="company_id.picking_operation_type", readonly=False)

    adj_operation_type = fields.Selection(default=lambda self: self.env.company.adj_operation_type,  string="Stock Adjustement Opration Type", related="company_id.adj_operation_type", readonly=False)

    scrap_operation_type = fields.Selection(default=lambda self: self.env.company.scrap_operation_type, string="Scrap Opration Type", related="company_id.scrap_operation_type",readonly=False)
    