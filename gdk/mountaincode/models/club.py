from odoo import models, fields


class Club(models.Model):
    _name = 'club'
    _description = 'Football Club Model'
    
    name = fields.Char(string='Football club', required=True)
    clubInfo = fields.Html(string='Introduction')
    player_ids = fields.One2many(comodel_name='player', inverse_name='club_id')