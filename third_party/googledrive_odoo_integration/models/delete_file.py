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

	@api.model
	def delete_googledrive_file(self,connection,file_map_ids):
		googledrive = connection.get('googledrive',False)
		url = connection.get('url','')
		access_token = connection.get('access_token',False)
		headers = {}
		data = ''
		return_vals = {}
		if url and access_token:
			headers.update({'Authorization': 'Bearer {}'.format(access_token)})
			for file_map_id in file_map_ids:
				file_id = file_map_id.file_id
				if file_id:
					status = self.delete_item_googledrive(connection,url,access_token,file_id,headers)
		return True			
	
	@api.model
	def delete_item_googledrive(self,connection,url, access_token,file_id,headers):
		url += file_id +"?key=%s"%connection.get('client_secret_key','')
		gdriveapi = connection.get('googledrive',False)
		status = False
		data = {}
		try:	
			response = gdriveapi.call_drive_api(url,'DELETE',data=data,headers=headers,files=None)
			status = True
		except:
			pass
		return status
