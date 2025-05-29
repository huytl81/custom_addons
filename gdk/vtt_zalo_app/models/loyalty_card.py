from odoo import api, fields, models

class LoyaltyCard(models.Model):
    _inherit = "loyalty.card"

    level_points = fields.Float('Level points', default=0)

    tier_id = fields.Many2one(
        comodel_name='vtt.loyalty.tier',
        string="Tier",
        compute='_compute_tier',
        store=True, readonly=False, required=True, precompute=True,
        # domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]"
    )

    @api.depends('level_points')
    def _compute_tier(self):
        if self.program_id and self.program_id.loyalty_tier_ids and len(self.program_id.loyalty_tier_ids):
            self.tier_id = self.program_id.loyalty_tier_ids[0]
            t = self.program_id.loyalty_tier_ids[0]
            for tier in self.program_id.loyalty_tier_ids:
                if self.level_points == tier.range_min:
                    t = tier
                    break
                if self.level_points >= tier.range_min and tier.range_max == -1:
                    t = tier
                    break
                if self.level_points >= tier.range_min and self.level_points <= tier.range_max:
                    if self.level_points == tier.range_max:
                        continue
                    t = tier
                    break
            self.tier_id = t
        else:
            self.tier_id = False

    # partner_invoice_id = fields.Many2one(
    #     comodel_name='res.partner',
    #     string="Invoice Address",
    #     compute='_compute_partner_invoice_id',
    #     store=True, readonly=False, required=True, precompute=True,
    #     domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    #
    # @api.depends('partner_id')
    # def _compute_partner_invoice_id(self):
    #     for order in self:
    #         order.partner_invoice_id = order.partner_id.address_get(['invoice'])['invoice'] if order.partner_id else False