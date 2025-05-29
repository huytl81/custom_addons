# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import requests


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    state_code = fields.Char('Mã tỉnh thành')  # ma theo quy dinh chung


