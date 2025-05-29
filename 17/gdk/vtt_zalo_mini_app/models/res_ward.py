from odoo import api, fields, models

class ResWard(models.Model):
    _inherit = 'res.ward'

    shipping_allowed = fields.Boolean('Cho phép giao hàng', default=False)
    default_shipping_method_price = fields.Float('Phí ship mặc định')
    code = fields.Char('Mã phường xã')

    # full_text_search = fields.Char('Full text search', compute='_compute_full_text_search', store=True)

    # @api.depends('state_id', 'district_id')
    # def _compute_full_text_search(self):
    #     for record in self:
    #         record.full_text_search = f'{record.name}, {record.district_id.name}, {record.state_id.name}'

    def allow_shipping(self):
        for record in self:
            record.shipping_allowed = True

    def disallow_shipping(self):
        for record in self:
            record.shipping_allowed = False

    def update_shipping_price(self):
        ab = self
        abc = 'a'

        return {
            'type': 'ir.actions.act_window',
            'name': 'Update Shipping Price',
            'res_model': 'update.shipping.price.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_shipping_price': 0,
                'active_ids': self.ids,
                'active_model': self._name,
            },
        }
    
    @api.depends('state_id', 'district_id', 'name')
    def _compute_display_name(self):
        # result = []
        for record in self:
            name = record.name + ' ('
            if record.district_id:
                name = f"{name} {record.district_id.name}"
            if record.state_id:
                name = f"{name}, {record.state_id.name}"      
            name = name + ')'      
            record.display_name = name
        #     result.append((record.id, name))
        # return result
    # @api.depends_context('input_full_display_name')
    # def _compute_display_name(self):
    #     for partner in self:
    #         context = partner.env.context
    #         name = partner.name
    #         if partner.phone:
    #             name = f"{name} ({partner.phone})"
    #         partner.display_name = name      