# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Player(models.Model):
    _name = "player"
    _description = "Player model"

    name = fields.Char(string="Name", required=True, translate=True)
    date_of_birth = fields.Date(string="Date of birth", required=True)
    image = fields.Image(string="Image", attachment=True)
    resume = fields.Binary(string="Resume", attachment=True)
    position = fields.Char(string="Position", groups='group_player_manager')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender")
    country = fields.Char(string="Country")
    weight = fields.Float(string="Weight", digits=(5,3))
    height = fields.Float(string="Height")
    transfer = fields.Float(string="Transfer Market")
    club_id = fields.Many2one(comodel_name='club')
    dog_ids = fields.Many2many(comodel_name='dog')