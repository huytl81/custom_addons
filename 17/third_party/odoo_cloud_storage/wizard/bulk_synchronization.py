# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import fields, models
from odoo.exceptions import UserError

connection  = 'cloud.odoo.connection'

class CloudBulkSynchronisation(models.TransientModel):
	_name = 'cloud.bulk.synchronisation'
	_description = "Cloud Bulk Synchronisation"

	def _default_instance_name(self):
		return self.env[connection].search([], limit=1).id

	action = fields.Selection(
		selection =[('import', 'Import File'), ('export', 'Export File')], 
		string='Action', 
		default="export", 
		required=True,
		readonly = True,
		help="""Import File: Import Files From Cloud. Export File:Export File To Cloud""")
	instance_id = fields.Many2one(
		comodel_name = connection, 
		string='Cloud Instance', 
		default=lambda self: self._default_instance_name())
	folder_id = fields.Many2one(
		comodel_name = 'cloud.folder.mapping',
		string = 'Select Folder')
	
	def start_action_cloud_synchronization(self):
		action = self.action
		folder_id = self.folder_id
		if folder_id:
			if action=='export':
				return folder_id.synchronise_folder_files()
			else:
				return folder_id.download_folder_files()
		else:
			raise UserError('Please Select Any Folder To Be Exported')
