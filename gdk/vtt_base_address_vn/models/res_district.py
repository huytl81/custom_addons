# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, _
from odoo.tools import file_open
import requests
import csv

_logger = logging.getLogger(__name__)


class ResDistrict(models.Model):
    _name = 'res.district'
    _description = 'District'
    _order = 'state_id'

    name = fields.Char("Name", required=True, translate=True)
    country_id = fields.Many2one('res.country', string='Country', required=True)
    state_id = fields.Many2one('res.country.state', 'State', domain="[('country_id', '=', country_id)]")
    # ghn_district_id = fields.Integer('GHN District ID', help='District ID for GHN delivery method')

    code = fields.Char('Mã Quận huyện')