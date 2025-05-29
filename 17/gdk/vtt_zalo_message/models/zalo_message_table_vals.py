from odoo import api, fields, models

class ZaloMessageTableVals(models.Model):
    _name = 'zalo.message.table.vals'
    _description = 'Zalo Message table vals'

    key = fields.Char(string='Label', required=True)
    value = fields.Char(string='Value', required=True)    
    template_id = fields.Many2one('zalo.message.template', string='Template', ondelete='cascade')
    # phuong an chon field co the se phải lam danh sach gia tri mau, co the la field selection vd: res_partner.name

    @api.model
    def create(self, vals):
        if 'template_id' not in vals and self.env.context.get('default_template_id'):
            vals['template_id'] = self.env.context['default_template_id']
        return super(ZaloMessageTableVals, self).create(vals)