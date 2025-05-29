# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, models
import logging
_logger = logging.getLogger(__name__)

class CloudSnippet(models.TransientModel):
	_inherit = 'cloud.snippet'

	@api.model
	def sync_attachment_cloud(self,connection, model,record_ids,folder_id,instance_id,storage_type):
		printmessage = ''
		message_wizard = self.env['cloud.message.wizard']
		odoo_file_env = self.env['cloud.odoo.file.mapping']
		file_ids = []
		file_urls = []
		successfull_ids = []
		unsuccessfull_ids = []
		attachment_ids = []
		domain = [
			('res_model','=',model),
			('res_id','in',record_ids),
			('res_field','=',False)
			]   
		file_env_rcrds = odoo_file_env.search([
			('record_id','in',record_ids),
			('state','=','done'),
			('folder_id','=',folder_id.id)
			])
		attachment_ids = file_env_rcrds.mapped('attachment_id').ids or []
		domain.append(('id','not in',attachment_ids))
		attachment_records = self.get_attachment_records(domain)
		if not attachment_records:
			message = 'No attachment found to Synchronise'
			return message_wizard.generate_message(message)
		for attachment in attachment_records:
			status, message, file_map_id = self.export_attachment_to_cloud(connection,attachment,instance_id,storage_type,folder_id)
			if status:
				successfull_ids.append(attachment.id)
			else:
				unsuccessfull_ids.append(message)
		if successfull_ids and not unsuccessfull_ids:
			printmessage = 'Successfull Synchronise Ids Are:{}'.format(successfull_ids)
		elif unsuccessfull_ids and not successfull_ids:
			printmessage = 'Unsuccessfull Synchronise Message:{}'.format(unsuccessfull_ids)
		else:
			printmessage = 'Successfull Synchronise Ids Are:{}'.format(successfull_ids) + \
				' And UnsuccessFull Synchronise Ids With Message:{}'.format(unsuccessfull_ids)
		return message_wizard.generate_message(printmessage)
	
	def export_attachment_to_cloud(self,connection,attachment,instance_id,storage_type,folder_id):
		status = False
		file_datas = {}
		message = 'Attachment Exported Successfully' 
		file_map_id,action,request_vals = self._get_request_vals(attachment,instance_id,storage_type,folder_id)
		if hasattr(self,'_%s_%s_attachment_cloud'%(action,storage_type)):## Need to define a function to export attachment like this _{action}_{storage_type}_attachment_cloud, here action can be export and update. 
			response_data = getattr(self,'_%s_%s_attachment_cloud'%(action,storage_type))(connection,instance_id,request_vals)
			
			status = response_data.pop('status',False)
			if status:
				state = 'done'
			else:
				message = response_data.get('message','Error For Attachment Record')\
						+ ' And Attachment ID=' + str(attachment.id)
				state = 'error'
		file_datas.update({
			'state':state,
			'record_folder_id':response_data.get('record_folder_id') \
					or request_vals.get('record_folder_id') or '',
			'record_folder_path':response_data.get('record_folder_path') \
				or request_vals.get('record_folder_path') or '',
			'record_folder_name': request_vals.get('folder_name','')
		})
		if response_data.get('file_id',False):
			file_datas.update({'file_id':response_data['file_id']})
		if response_data.get('file_url',False):
			file_datas.update({'file_url':response_data['file_url']})
		if file_map_id:
			if file_map_id.file_id and state=='error':
				state = file_datas.pop('state',False)
			file_map_id.write(file_datas)
		else:
			file_datas.update({
				'folder_id':folder_id.id,
				'instance_id':instance_id,
				'record_id':attachment.res_id,
				'attachment_id':attachment.id,
				})
			file_map_id = self.create_file_mapping(file_datas,storage_type,'cloud.odoo.file.mapping')
			if file_map_id:
				file_map_id.message = message
		return status, message, file_map_id
	
	@api.model
	def _get_request_vals(self,attachment,instance_id,storage_type,folder_id): 
		file_map_id = False
		odoo_file_env = self.env['cloud.odoo.file.mapping']
		request_vals = {
			'folder_id':folder_id.folder_id,
			'folder_path':folder_id.folder_path
			}
		attachment_datas, full_path, mime_type,folder_name, file_size = self._get_attachment_data(attachment)
		
		request_vals.update({
			'file_data':attachment_datas,
			'file_path': full_path,
			'folder_name':folder_name,
			'mime_type':mime_type,
			'file_size':file_size,
			'create_folder':True,
			'file_name':attachment.name
			})
		action = 'export'
		file_map_id = odoo_file_env.search([
			('attachment_id','=',attachment.id),
			('instance_id','=',instance_id),
			('folder_id','=',folder_id.id)
			],
			limit=1)
		if file_map_id.file_id and file_map_id.state == "need_sync":
			request_vals.update({
				'file_id':file_map_id.file_id,
				'file_url':file_map_id.file_url,
				'record_folder_id':file_map_id.record_folder_id,
				'record_folder_path':file_map_id.record_folder_path
				})
			action = 'update'
		if hasattr(self, 'get_%s_attachment_data' %storage_type):## If you will need some extra data to create and update 
			updated_request_vals = getattr(self, 'get_%s_attachment_data' %storage_type)(instance_id,request_vals,
			folder_id,attachment, file_map_id)
			request_vals.update(updated_request_vals)
		if action=='export':
			record_id = attachment.res_id
			create_folder = odoo_file_env.search([
				('record_id','=',record_id),
				('instance_id','=',instance_id),
				('folder_id','=',folder_id.id),
				('record_folder_id','not in',[False,''])
				],limit=1)
			if create_folder.record_folder_id:
				request_vals.update({
					'create_folder':False,
					'record_folder_id':create_folder.record_folder_id,
					'record_folder_path':create_folder.record_folder_path
					})
		
		return file_map_id,action,request_vals

	@api.model
	def get_attachment_records(self,domain):
		'''This function use to get attachment records
			@params
			domain --attachment domain
			@returns
			attahcment records
		'''
		context = self._context.copy() or {}
		context.update({'from_filestore':False})
		self = self.with_context(context)
		export_limit = self.env['res.config.settings'].cloud_config_limit()
		attachment_env = self.env['ir.attachment']
		attachment_record = attachment_env.search(domain,limit=export_limit)
		return attachment_record

	@api.model
	def _get_attachment_data(self,attachment_obj):
		'''This function use to get attachment data
		@params
			attachment_obj --> Attachment's Object
		@returns
		attachment_dats :- Binary data of attachment
		path:- If attachment's type is binary then retuns file store path
		mime_type :- Mime Type Of File
		Folder name:- Folder Name to Be Created For Records
		'''
		fname = attachment_obj.store_fname or False
		file_size =  attachment_obj.file_size
		mime_type = attachment_obj.mimetype or 'text/plain'
		path = ''
		
		if fname:
			attachment_datas = attachment_obj._file_read(fname)
			
			path = attachment_obj._full_path(fname)
			
		else:
			attachment_datas = attachment_obj.db_datas
		if attachment_obj.res_name:
			folder_name = attachment_obj.res_name + 'id' +str(attachment_obj.res_id)
			folder_name = ''.join(folder for folder in folder_name if folder.isalnum())
		else:
			folder_name = 'core_attachment'
		if not attachment_datas:
			attachment_datas = self._context.get('file_data','')
			

		return attachment_datas, path, mime_type, folder_name, file_size

