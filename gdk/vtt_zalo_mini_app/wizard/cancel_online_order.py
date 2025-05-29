from odoo import api, fields, models

class CancelOnlineOrderWizard(models.TransientModel):
    _name = 'cancel.online.order.wizard'
    _description = 'Wizard Hủy Đơn Hàng'

    cancel_reason = fields.Text('Chọn lý do')
    reason = fields.Selection([
        ('customer_cancel', 'Khách hàng hủy đơn'),
        # ('out_of_stocks', 'Không có hàng'),
        # ('cannot_delivery', 'Không giao hàng được'),
        ('company_cancel', 'Cửa hàng hủy đơn'),
        ('other', 'Khác'),
    ], string='Lý do cụ thể', default='customer_cancel')

    partner_id = fields.Many2one('res.partner', string='Khách hàng')
    # partner_ids = fields.Many2many('res.partner', string='Khách hàng')

    @api.onchange('reason')
    def _onchange_reason(self):
        if self.reason:
            if self.reason == 'customer_cancel':
                self.cancel_reason = 'Khách hàng hủy đơn hàng'
            # elif self.reason == 'out_of_stocks':
            #     self.cancel_reason = 'Không có hàng'
            elif self.reason == 'company_cancel':
                self.cancel_reason = 'Cửa hàng hủy đơn'
            elif self.reason == 'other':
                self.cancel_reason = ''

    def action_cancel_order(self):
        sale_order = self.env['sale.order'].browse(self.env.context.get('active_id'))
        sale_order.cancel_reason_for_customer = self.cancel_reason
        sale_order._action_cancel()
        return {'type': 'ir.actions.act_window_close'}