from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_loyalty_member_reward = fields.Boolean('Is loyalty member reward', default=False)
    is_percent_value = fields.Boolean('Is percent value', default=False)
    loyalty_member_reward_value = fields.Float('Loyalty member reward value', default=0)   # unit | percent
    is_delivery_fee_line = fields.Boolean('Is delivery fee line', default=False)