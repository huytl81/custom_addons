# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

import requests
from odoo import _, api, fields, models
import json
from werkzeug import urls
from logging import getLogger
_logger = getLogger(__name__)

TIMEOUT = 20

GOOGLE_AUTH_ENDPOINT = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_TOKEN_ENDPOINT = 'https://accounts.google.com/o/oauth2/token'
GOOGLE_API_BASE_URL = 'https://www.googleapis.com'

def _unescape(text):
	##
	# Replaces all encoded characters by urlib with plain utf8 string.
	#
	# @param text source text.
	# @return The plain text.
	from urllib.parse import unquote_plus
	try:
		text = unquote_plus(text)
		return text
	except Exception as e:
		return text

class CloudOdooConnection(models.Model):
	_inherit = 'cloud.odoo.connection'

	api_token = fields.Text('Access Token')
	refresh_token = fields.Text('Refresh Token')

	@api.model
	def _get_storage_types(self):
		storage_type = super()._get_storage_types()
		storage_type.append(('googledrive','Google Drive'))
		return storage_type
	
	@api.model
	def get_dashboard_googledrive_data(self,row):
		connection_obj = self.browse(row['id'])
		row['icon'] = '/googledrive_odoo_integration/static/src/img/googledrive.png'
		row['url'] = self.env['cloud.snippet'].get_googledrive_base_url(connection_obj)
		return row



	def get_google_scope(self):
		return 'https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/drive.file'
	

	# This method is resposible for generating the authorization_code(access_token) using the crenditials.json
	# which is generated from Google API Console (OAuth 2.0 Client IDs ,web client
	# file containes - > client_id,scope,client_secret_key


	def test_googledrive_connection(self):
		gen_message = self.env['cloud.message.wizard']
		client_id = self.api_key
		clien_secret_key = self.api_password
		redirect_uri = self.api_url
		scope = self.get_google_scope()
		headers = {'Content-Type':'application/x-www-form-urlencoded'}
		data = {
			'client_id':client_id,
			'scope':scope,
			'response_type':'code',
			'redirect_uri':redirect_uri,
			'approval_prompt': 'force', #in case if request approval from client everytime[testconnection] then only refresh token is generated
			'access_type': 'offline'
		}
		encoded_data = urls.url_encode(data)
		url = '%s?%s' % (GOOGLE_AUTH_ENDPOINT,encoded_data)
		res = requests.get(url,headers=headers)
		if res.status_code in [200,201]:
			return {
				'name'	   : 'Go to Google Drive',
				'res_model': 'ir.actions.act_url',
				'type'     : 'ir.actions.act_url',
				'target'   : 'new',
				'url'      :  url
				}
		else:
			message = """Issue: Error While Getting Authorisation Code(Url Not Found)"""
			self.write({
				'connection_status' : False
			})
		return gen_message.generate_message(message)
	
	# This method is resposible for generating refresh_token using  the authorization_code(access_token) 
	@api.model
	def _create_googledrive_flow(self,instance_id,*args,**kwargs):
		status = True
		headers = {'Content-Type':'application/x-www-form-urlencoded'}
		instance_obj = self.browse(instance_id)
		client_id = instance_obj.api_key
		clien_secret_key = instance_obj.api_password
		redirect_uri = instance_obj.api_url
		error = ''
		authorization_code = kwargs.get('code','')
		url = GOOGLE_TOKEN_ENDPOINT = 'https://accounts.google.com/o/oauth2/token'
		message = 'Access Token And Refresh Token Successfully Updated'
		data = {
			'client_id':client_id,
			'redirect_uri':redirect_uri,
			'client_secret':clien_secret_key,
			'code':authorization_code,
			'grant_type':'authorization_code'
			}
		try:
			gdriveapi = self.env['call.googledrive.api']
			response = gdriveapi.call_drive_api(url,'POST',data=data,headers=headers,files=None)
			# req = requests.post(GOOGLE_TOKEN_ENDPOINT, data=data, headers=headers, timeout=TIMEOUT)
		except Exception as e:
			status = False
			message = str(e)
		if status:
			if 'refresh_token' in response:
				instance_obj.refresh_token = response['refresh_token']
			if 'access_token' in response:
				instance_obj.api_token = response['access_token']
		vals={
			'message':message,
			'connection_status':status
		}
		instance_obj.write(vals)
		return{
			'status':status
		}

	#this method is responsible for creating connection , generating new access token using the refresh token
	@api.model
	def _create_googledrive_connection(self, instance_id,refresh_token = False):
		context = self._context.copy() or {}
		context.update({'instance_id':instance_id})
		self = self.with_context(context)
		instance_obj = self.browse(instance_id)
		context['instance_obj'] = instance_obj
		gdriveapi = self.env['call.googledrive.api']
		return_data={}
		status = True
		url = GOOGLE_TOKEN_ENDPOINT = 'https://accounts.google.com/o/oauth2/token'
		error = ''
		client_id = instance_obj.api_key
		access_token = instance_obj.api_token
		if refresh_token:
			headers = {
				'Content-Type': 'application/x-www-form-urlencoded'
				}
			scope = 'https://www.googleapis.com/auth/drive'
			#For Getting New Access Token With help of old Refresh Token
			data = {
			'client_id' : client_id,
			'client_secret':instance_obj.api_password,
			'refresh_token':instance_obj.refresh_token, #
			'grant_type':'refresh_token',
			'scope': scope
			}
			try:
				response = gdriveapi.call_drive_api(url,'POST',data=data,headers=headers,files=None)
				# req = requests.post(GOOGLE_TOKEN_ENDPOINT,data=data,headers=headers,timeout=TIMEOUT)
			except Exception as e:
				error = str(e)
			if status:
				if 'access_token' in response:
					access_token = response['access_token']
				if 'refresh_token' in response:
					refresh_token = response['refresh_token']
				if context.get('refresh_token',True):
					instance_obj.write({'api_token':access_token})
					if 'refresh_token' in response:
						instance_obj.write({'refresh_token':refresh_token})
		return{
			'url': 'https://www.googleapis.com/drive/v3/files/',
			'client_secret_key':instance_obj.api_password,
			'instance_id':instance_id,
			'googledrive':gdriveapi,
			'access_token':access_token,
			'status':status,
			'error' : error
			}

	def create_googledrive_folder(self,connection,instance_obj,vals):
		access_token = connection.get('access_token',False)
		url = connection.get('url','')
		gdriveapi = connection.get('googledrive',False)
		status = False
		message = 'Error:Error While Creating Folder In googledrive'
		headers = {
			'Authorization': 'Bearer {}'.format(instance_obj.api_token), # your access token 
			'Content-Type': 'application/json'
		}
		return_vals = {}	
		if access_token and url:
			body = {
				'name': instance_obj.cloud_folder_name, #folder_name as a string
				'mimeType': 'application/vnd.google-apps.folder',
			}
			file_metadata = json.dumps(body)
			# ================================== REST API =========================
			# Google Drive API wants the needed parameters in 
			# {request body} that is a request body with folder name and mime type as 'application/vnd.google-apps.folder', so metadata must be passed as json string 
			# and header "content-type" carefully set to "application/json", otherwise the API will not like 
			# very much python requests default to 'application/x-www-form-urlencoded'
			# ====================================================================
			try:
				response = gdriveapi.call_drive_api(url,'POST',data=file_metadata,headers=headers,files=None)
				# req = requests.post(url, headers = headers, data = file_metadata)
				a = {
					'kind': 'drive#file', 
					'id': '171EYXojv3Fl1fKZaYO86dhUkHi2to-JE', 
					'name': 'odoo_issues1', 
					'mimeType': 'application/vnd.google-apps.folder'
					} 
				status = True
			except Exception as e:
				message ='Error:' + str(e)
			if status:
				message = 'Folder Successfully Created In GoogleDrive'
				return_vals.update({
					'folder_id':response.get('id','')
				})
				if return_vals['folder_id']:
					return_vals['folder_path'] = 'https://drive.google.com/drive/folders/%s'%return_vals['folder_id']
		return_vals.update({
			'status':status,
			'message':message
		})
		return return_vals



	def	update_googledrive_folder(self,connection,instance_id,vals):
		access_token = connection.get('access_token',False)
		url = connection.get('url','')
		gdriveapi = connection.get('googledrive',False)
		status = True
		message = 'Error:Error While Updating Folder In GoogleDrive'
		return_vals = {}
		if access_token and url:
			headers = {
				'Authorization': 'Bearer {}'.format(access_token),
				'Content-Type': 'application/json'
				}
			file_id = vals.get('folder_id',False)
			if file_id:
				url += file_id + '?key={}'.format(self.api_password)
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
				message ='Error' + str(e)
			if status:
				message = 'Folder Successfully Updated In GoogleDrive'
		return_vals.update({
			'status':status,
			'message':message
		})
		return return_vals