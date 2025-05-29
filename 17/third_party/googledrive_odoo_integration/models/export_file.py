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
import base64
import logging
_logger = logging.getLogger(__name__)

class CloudSnippet(models.TransientModel):
	_inherit = 'cloud.snippet'

	def sync_parent_folder(self,connection,instance_id,request_vals):
		create = request_vals.get('create_folder',True)
		status = True
		message = 'File Successfully Synchronised'
		if create:
			vals = {
				'folder_name':request_vals.get('folder_name'),
				'parent_folder_id':request_vals.get('folder_id')
				}
			response = self.create_googledrive_folder(connection,instance_id,vals)
			status = response.get('status')
			message = response.get('message')
			if status:
				request_vals.update({
						'record_folder_id':response.get('folder_id',False),
						'record_folder_path':response.get('folder_path',False)
					})
		request_vals.update({
			'status':status,
			'message':message
		})
		return request_vals


	def _export_googledrive_attachment_cloud(self,connection,instance_id,request_vals):
		message = 'Error:Issue While Creating Folder In Odoo'
		return_vals = {}
		request_vals = self.sync_parent_folder(connection,instance_id,request_vals)
		status = request_vals.get('status')
		message = request_vals.get('message')
		if status:
			return_vals.update({
					'record_folder_id':request_vals.get('record_folder_id'),
					'record_folder_path':request_vals.get('record_folder_path')
					})
			response_vals = self.sync_googledrive_attachment(connection,instance_id,request_vals)
			
			status = response_vals.get('status')
			message = response_vals.get('message')
			if status:
				return_vals.update({
					'file_id':response_vals.get('file_id'),
					'record_folder_id':request_vals.get('record_folder_id'),
					'record_folder_path':request_vals.get('record_folder_path'),
					'file_url' : response_vals.get('file_url','')
					})
		return_vals.update({
			'status':status,
			'message':message
		})
		
		return return_vals
				
	
	def sync_googledrive_attachment(self,connection,instance_id,request_vals):
		access_token = connection.get('access_token',False)
		gdriveapi = connection.get('googledrive',False)
		# url = connection.get('url','')
		status = False
		url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
		message = 'Error:Issue While Creating Folder In Odoo'
		return_vals = {}	
		if access_token and url:
			file_name = request_vals.get('file_name')
			parent_folder_id = request_vals.get('record_folder_id')
			full_path = request_vals.get('file_path')
			file_content = request_vals.get('file_data')
			# content = base64.b64decode(file_content)
			content = file_content
			content_type = request_vals.get('mime_type')
			headers = {
				'Authorization': 'Bearer {}'.format(access_token),
				}
			body = {
				'name': file_name, #folder_name as a string
			}
			if parent_folder_id:
				body['parents'] = [parent_folder_id]
			files = {
				'data': ('metadata', json.dumps(body),'application/json; charset=UTF-8'),
				'file': (content_type,content)
				}
			data = {}
			try:
				response = gdriveapi.call_drive_api(url,'POST',data=data,headers=headers,files=files)
				# response = requests.post(url,files=files,headers=headers)
				status = True
			except Exception as e:
				message ='Error:' + str(e)
			if status:
				message = 'Folder Successfully Created In GoogleDrive'
				return_vals.update({
					'file_id':response.get('id')
					})
				if return_vals['file_id']:
					return_vals['file_url'] = 'https://drive.google.com/file/d/%s/view'%return_vals['file_id']
		return_vals.update({
			'status':status,
			'message':message
		})
		return return_vals


	def _update_googledrive_attachment_cloud(self,connection,instance_id,request_vals):
		access_token = connection.get('access_token',False)
		gdriveapi = connection.get('googledrive',False)
		status = False
		url = connection.get('url',False)
		message = 'Error:Issue While Updating Attachment In Goole Drive'
		return_vals = {}
		if access_token and url:
			file_id = request_vals.get('file_id')
			if file_id:
				# content = base64.b64decode(request_vals.get('file_data'))
				content  = request_vals.get('file_data')
				content_type = request_vals.get('mime_type')
				file_name = request_vals.get('file_name')
				headers = {
				'Authorization': 'Bearer {}'.format(access_token),
				'Content-Type': 'application/json'
				}
				if file_id:
					url += file_id + '?key={}'.format(self.env['cloud.odoo.connection'].browse(instance_id).api_password)
				body = {
					'name':file_name,
					}
				data = json.dumps(body)
				try:
					response = gdriveapi.call_drive_api(url,'PATCH',data=data,headers=headers,files=None)
					# response = requests.patch(url,headers = headers,data = data)
					status = True
				except Exception as e:
					message ='Error:' + str(e)
				if status:
					message = 'Attachment Successfully Updated In GoogleDrive'
		return_vals.update({
			'status':status,
			'message':message
		})
		return return_vals