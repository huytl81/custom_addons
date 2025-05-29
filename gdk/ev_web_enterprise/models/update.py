# -*- coding: utf-8 -*-

import logging
from odoo.models import AbstractModel
from odoo.exceptions import UserError
from odoo import SUPERUSER_ID
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class PublisherWarrantyContract(AbstractModel):
    _inherit = "publisher_warranty.contract"

    def update_notification(self, cron_mode=True):
        set_param = self.env['ir.config_parameter'].sudo().set_param

        new_date = datetime.now() + timedelta(days=365)

        set_param('database.expiration_date', new_date)
        set_param('database.expiration_reason', 'renew')
        set_param('database.enterprise_code', 'VTT_RENEWING')
        # set_param('database.already_linked_subscription_url',
        #           result['enterprise_info'].get('database_already_linked_subscription_url'))
        # set_param('database.already_linked_email', result['enterprise_info'].get('database_already_linked_email'))
        # set_param('database.already_linked_send_mail_url',
        #           result['enterprise_info'].get('database_already_linked_send_mail_url'))

        return True