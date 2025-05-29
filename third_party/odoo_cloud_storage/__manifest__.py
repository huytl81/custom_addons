# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Odoo Cloud Storage",
  "summary"              :  """To Store Odoo Attachments On Cloud, Storage, Cloud Solution, like, Google Drive, OneDrive, Connector, Bridge, Nextcloud, Box""",
  "category"             :  "CLOUD",
  "version"              :  "2.1.9",
  "sequence"             :  1,
  "license"              :  "Other proprietary",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "website"              :  "https://store.webkul.com/Odoo-Cloud-Storage.html",
  "description"          :  """Cloud Storage Odoo Integration
==============================
This module connects your between the Odoo and Cloud Storage and allows synchronization attachement between them 

 

For any doubt or query email us at support@webkul.com or raise a Ticket on http://webkul.com/ticket/""",
  "depends"              :  [
                             'sale_stock',
                             'delivery',
                             'mail',
                             'wk_wizard_messages',
                            ],
  "data"                 :  [
                             'data/mail_data.xml',
                             'data/cloud_storage_cron.xml',
                             'security/storage_security.xml',
                             'security/ir.model.access.csv',
                             'wizard/bulk_synchronisation_view.xml',
                             'wizard/cloud_message_wizard_view.xml',
                             'wizard/cloud_synchronization_wizard_view.xml',
                             'views/cloud_folder_mapping_view.xml',
                             'views/cloud_odoo_file_mapping_view.xml',
                             'views/cloud_odoo_connection_view.xml',
                             'views/cloud_dashboard.xml',
                             'views/cloud_base_menus.xml',
                             'views/res_config_view.xml',
                            ],
    'assets': {
        'web.assets_backend': [
                '/odoo_cloud_storage/static/src/js/chatter.js',
                # '/odoo_cloud_storage/static/src/js/attachment_box.js',
                '/odoo_cloud_storage/static/src/js/cloud_dashboard.js',
                '/odoo_cloud_storage/static/src/scss/cloud_kanban.scss',
                '/odoo_cloud_storage/static/src/scss/dashboard.scss',
                '/odoo_cloud_storage/static/src/xml/thread.xml',
                '/odoo_cloud_storage/static/src/xml/chatter.xml',
                '/odoo_cloud_storage/static/src/xml/cloud_dashboard_template.xml',

        ],
        # 'web.assets_qweb': [
        #         '/odoo_cloud_storage/static/src/xml/thread.xml',
        #         '/odoo_cloud_storage/static/src/xml/chatter.xml',
        #         '/odoo_cloud_storage/static/src/xml/cloud_dashboard_template.xml',
        # ],
    },
  "images"               :  ['static/description/banner.gif'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  99,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
  "live_test_url"        :  "https://odoodemo.webkul.com/demo_feedback?module=odoo_cloud_storage"
}
