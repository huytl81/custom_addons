from odoo import api, fields, models

class VttLoyaltyTierReward(models.Model):
    _name = "vtt.loyalty.tier.reward"

    name = fields.Char(string='Name')
    value = fields.Float('Giá trị')
    value_type = fields.Selection([('unit', 'Đơn vị'), ('percent', '%')], string='Tính theo', default='unit')
    sequence = fields.Integer('Thứ tự áp dụng') # Su dung de sap xep ap dung phan thuong nao truoc

    tier_id = fields.Many2one('vtt.loyalty.tier', 'Hạng')