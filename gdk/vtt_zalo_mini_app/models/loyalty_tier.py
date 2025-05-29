from odoo import api, fields, models

# Tier chỉ phục vụ cho loyalty, áp dụng phần thưởng đơn giản là chiết khấu/giảm giá
class VttLoyaltyTier(models.Model):
    _name = "vtt.loyalty.tier"

    name = fields.Char(string='Name')
    description = fields.Text(string='Zalo description')
    range_min = fields.Float('Min', default=0)
    range_max = fields.Float('Max', default=0)
    level = fields.Integer('Level', default=1)
    next_level_id = fields.Integer('Next level', default=-1)

    # tier rewards
    # tao vtt.loyalty.tier.reward
    # fields: name, value, value_type (unit,percent), sequence (de sap xep tinh toan truoc sau)
    # rule tinh toan: se dua tren sequence ma tinh toan, gọi là phần thưởng nào áp dụng trước, áp dụng sau
    tier_reward_ids = fields.One2many('vtt.loyalty.tier.reward', 'tier_id', 'Tier rewards')

    # De thong nhat rule tinh diem
    loyalty_program_id = fields.Many2one('loyalty.program', 'Loyalty Program')


    # display
    sequence = fields.Integer('Sequence')
    color = fields.Char(string='Color')
    icon = fields.Image('Image', store=True)
