# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, models

class CloudSnippet(models.TransientModel):
	_inherit = 'cloud.snippet'

	def get_googledrive_folder_url(self,folder_id):
		return folder_id.folder_path if folder_id and folder_id.folder_path else '#'
	
	def get_googledrive_base_url(self,connection_obj):
		return connection_obj.cloud_folder_path if connection_obj and connection_obj.cloud_folder_path else '#'
	
	@api.model
	def get_googledrive_file_url(self,file_map_id, instance_id):
		return file_map_id.record_folder_path if file_map_id and file_map_id.record_folder_path else '#'
