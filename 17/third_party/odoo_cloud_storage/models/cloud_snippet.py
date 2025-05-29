# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api,models
import logging
_logger = logging.getLogger(__name__)

class CloudSnippet(models.TransientModel):
	_name = 'cloud.snippet'
	_description = 'Transient model For Snippet Of Cloud Module'

	
	def create_file_mapping(self, response_data,storage_type,model):
		'''This function is use to create file mapping
		@params
			response data --> dictionary of values
			storage_type --> storage type
			model --> model to create mappings like sale.order,res.partner
		@returns
		newly created model obj
		'''
		if hasattr(self,'_extend_%s_mapping'%storage_type):## if you want to update dictionary then you can define this function _extend_{storage_type}_mapping
			response_data = getattr(self,'_extend_%s_mapping'%storage_type)(response_data,model)
		res = self.env[model].create(response_data)
		return res
	

	@api.model
	def upload_attachment_to_cloud(self):
		'''Function called by cron to upload attachents to cloud'''
		folder_ids = self.get_folder_ids()
		for folder_id in folder_ids:
			folder_id.synchronise_folder_files()
			self._cr.commit()
		return True
	
	@api.model
	def download_attachment_from_cloud(self):
		'''Function called by cron to dowload attachmets from cloud'''
		folder_ids = self.get_folder_ids()
		for folder_id in folder_ids:
			folder_id.download_folder_files()
			self._cr.commit()
		return True
	
	@api.model
	def get_folder_ids(self):
		folder_map = self.env['cloud.folder.mapping']
		domain = [('run_cron','=',True),('state','=','done')]
		folder_ids = folder_map.search(domain)
		return folder_ids


