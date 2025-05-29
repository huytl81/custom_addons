# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################
from odoo import _, api, models
import json

class CloudSnippet(models.TransientModel):
	_inherit = 'cloud.snippet'

	def create_googledrive_folder(self, connection, instance_id, vals):
		# File ID is important as Google Drive uses file ID to specific the location instead of using file path.
		access_token = connection.get('access_token',False)
		gdriveapi = connection.get('googledrive',False)
		status = False
		url = connection.get('url','')
		message = 'Error:Issue While Creating Folder In Odoo'
		return_vals = {}
		if access_token and url:
			headers = {
				'Authorization': 'Bearer {}'.format(access_token),
				'Content-Type': 'application/json'
				}
			folder_name = vals.get('folder_name',False)
			parent_folder_id = vals.get('parent_folder_id',False)
			body = {
				'name':folder_name,
				'mimeType': 'application/vnd.google-apps.folder',
				}
			if parent_folder_id:
				body['parents'] = [parent_folder_id]
			file_metadata = json.dumps(body)
			try:
				response = gdriveapi.call_drive_api(url,'POST',data=file_metadata,headers=headers,files=None)
				# req = requests.post(url, headers = headers, data = file_metadata)														
				status = True
			except Exception as e:
				message ='Error:' + str(e)
			if status:
				# response = req.json()
				message = 'Folder Successfully Created In GoogleDrive'
				return_vals.update({'folder_id':response.get('id','')})
				if return_vals['folder_id']:
					return_vals['folder_path'] = 'https://drive.google.com/drive/folders/%s'%return_vals['folder_id']
		return_vals.update({
			'status':status,
			'message':message
		})
		return return_vals
	

	def	update_googledrive_folder(self,connection,instance_obj,vals):
		context = self._context.copy() or {}
		access_token = connection.get('access_token',False)
		gdriveapi = connection.get('googledrive')
		status = False
		url = connection.get('url','')
		message = 'Error:Error While Udating Folder In GoogleDrive'
		return_vals = {}	
		if access_token and url:
			headers = {
				'Authorization': 'Bearer {}'.format(access_token),
				'Content-Type': 'application/json'
				}
			folder_name = vals.get('folder_name')
			file_id = vals.get('folder_id')
			if file_id:
				url += file_id + '?key={}'.format(instance_obj.api_password)
			body = {
				'name':vals.get('folder_name'),
				'mimeType': 'application/vnd.google-apps.folder',
				}
			file_metadata = json.dumps(body)
			try:
				response = gdriveapi.call_drive_api(url,'PATCH',data=file_metadata,headers=headers,files=None)
				# response = requests.patch(url,headers = headers,data = file_metadata)
				status = True
			except Exception as e:
				message ='Error:' + str(e)
			if status:
				message = 'Folder Successfully Updated In GoogleDrive'
		return_vals.update({
			'status':status,
			'message':message
		})
		return return_vals
