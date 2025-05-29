from odoo import api, fields, models

class VttLoyaltyTierReward(models.Model):
    _name = "vtt.loyalty.tier.reward"

    name = fields.Char(string='Name')
    value = fields.Float('Min')
    value_type = fields.Selection([('unit', 'Đơn vị'), ('percent', '%')], default='unit')
    sequence = fields.Integer('Sequence') # Su dung de sap xep ap dung phan thuong nao truoc

    tier_id = fields.Many2one('vtt.loyalty.tier', 'Tier')