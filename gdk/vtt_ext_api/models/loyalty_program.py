from odoo import api, fields, models

class LoyaltyProgram(models.Model):
    _inherit = "loyalty.program"

    # auto apply when create order from Zalo
    auto_apply = fields.Boolean('Auto apply', default=False)
    is_zalo_loyalty_program = fields.Boolean('Is zalo loyalty program', default=False)

    # end_point = fields.Float('End point')
    level = fields.Integer('Card level') # OLD

    description = fields.Text(string='Zalo description')
    image = fields.Image('Image', store=True)

    loyalty_tier_ids = fields.One2many('vtt.loyalty.tier', 'loyalty_program_id', 'Loyalty tiers')

    loyalty_program_apply_id = fields.Many2one('loyalty.program', index=True, ondelete='cascade', domain=[('program_type', '=', 'loyalty')])
    required_points = fields.Float('Required points', default=0)  # su dung de doi thuong
    init_points = fields.Float('Init points', default=1)           # du kien su dung de so luong su dung (vd doi 100 diem dc 5 lan su dung)

    # phuc vu giao dien quy doi diem
    exchange_money = fields.Integer('Ex money', default=1)
    exchange_points = fields.Float('Ex points', default=1)

    @api.onchange('exchange_money', 'excahnge_points')
    def _onchange_exchange_points(self):
        """ Khi co su thay doi se cap nhat vao Rule + Reward cua Odoo loyalty default """
        if self.is_zalo_loyalty_program == True:
            if self.exchange_money > 0 and self.exchange_points > 0:
                ex_points = self.exchange_points / self.exchange_money
                if self.rule_ids and len(self.rule_ids) > 0:
                    rule = self.rule_ids[0]
                    rule.reward_point_amount = ex_points

    @api.onchange('is_zalo_loyalty_program')
    def _onchange_is_zalo_loyalty_program(self):
        """ Khi tick la chuong trinh the KH than thiet zalo """
        if self.is_zalo_loyalty_program == True:
            if self.rule_ids and len(self.rule_ids) > 0:
                rule = self.rule_ids[0]
                # reset default zalo loyalty rule
                rule.minimum_qty = 0
                rule.minimum_amount = 1
                rule.reward_point_mode = 'money'

                if self.exchange_money > 0 and self.exchange_points > 0:
                    ex_points = self.exchange_points / self.exchange_money
                    rule.reward_point_amount = ex_points


    def write(self, values):
        result = super().write(values)
        level = 1
        pre_tier = None
        for tier in self.loyalty_tier_ids:
            tier.level = level
            tier.next_level_id = -1
            level += 1

            if pre_tier:
                pre_tier.next_level_id = tier.id
            pre_tier = tier

        return result

    # @api.onchange('loyalty_tier_ids')
    # def _onchange_tier(self):
    #     level = 1
    #     pre_tier = None
    #     for tier in self.loyalty_tier_ids:
    #         tier.level = level
    #         tier.nxt_lvl_id = level+1
    #         tier.nextlvl = level + 2
    #         level+=1
    #
    #         if pre_tier and not tier.id.ref:
    #             id = tier.id
    #             idd = tier.id.origin
    #             pre_tier.nxt_lvl_id = idd
    #
    #         pre_tier = tier

