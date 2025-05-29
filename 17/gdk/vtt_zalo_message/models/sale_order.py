import datetime
import requests

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import json

class SaleOrder(models.Model):
    _inherit = "sale.order"

    # khi KH xac nhan
    def customer_confirm(self):
        res = super().action_delivering()

        return res

    def action_delivering(self):
        res = super().action_delivering()

        return res

    def action_done(self):
        res = super().action_done()

        return res

    def action_paid(self):
        res = super().action_paid()
        return True


    def action_confirm(self):
        res = super().action_confirm()

        self.env['zalo.message.template'].sudo().send_zns_transaction_message(order=self, event='order_confirmed')

        return res

    def _action_cancel(self):
        res = super()._action_cancel()        

        return res

    def action_draft(self):
        res = super().action_draft()

        return res