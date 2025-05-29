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
  "name"                 :  "Google Drive Odoo Integration",
  "summary"              :  """Bi-directional synchronization with Google Drive""",
  "category"             :  "cloud",
  "version"              :  "1.1.4",
  "sequence"             :  1,
  "license"              :  "Other proprietary",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "website"              :  "https://store.webkul.com/odoo-google-drive-integration.html",
  "description"          :  """Google Drive Odoo integration
==============================
This module establish integration between your Odoo and Google Drive  and allows bi-directional synchronization
 of your atachments between them.

NOTE: You need to install a corresponding 'odoo cloud storage' plugin too,
in order to work this module perfectly.

For any doubt or query email us at support@webkul.com or raise a Ticket on http://webkul.com/ticket/""",
  "depends"              :  ['odoo_cloud_storage'],
  "data"                 :  [
                              'security/ir.model.access.csv',
                              'views/cloud_odoo_connection_view.xml'
                            ],
  "images"               :  ['static/description/banner.gif'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  100,
  "currency"             :  "USD",
  "external_dependencies":  {'python': ['requests']},
  "live_test_url"        : "https://odoodemo.webkul.com/demo_feedback?module=googledrive_odoo_integration",
}