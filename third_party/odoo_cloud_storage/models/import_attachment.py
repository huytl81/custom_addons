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
	def import_attachment_cloud(self,connection, model,record_ids,instance_id,storage_type,folder_id):
		printmessage = ''
		message_wizard = self.env['cloud.message.wizard']
		odoo_file_env = self.env['cloud.odoo.file.mapping']
		file_ids = []
		file_urls = []
		successfull_ids = []
		unsuccessfull_ids = []
		attachment_ids = []
		exported_records = {}
		message = 'Error:Error While Importing Attachment From Cloud'
		records = odoo_file_env.search([
			('record_id','in',record_ids),
			('folder_id','=',folder_id)])
		read_fiels = self.get_fields()
		if records:
			read_data = records.read(read_fiels)
			for data in read_data:
				record_folder_id = data['record_folder_id']
				if record_folder_id:
					if record_folder_id in exported_records:
						exported_records[record_folder_id]['file_ids'].append(data['file_id'])
						exported_records[record_folder_id]['file_urls'].append(data['file_url'])
					else:
						exported_records[record_folder_id]= {
							'record_id':data['record_id'],
							'model' : model,
							'record_folder_name':data['record_folder_name'],
							'record_folder_path':data['record_folder_path'],
							'record_folder_id':data['record_folder_id'],
							'file_ids':[data['file_id']],
							'file_urls':[data['file_url']]}
					if hasattr(self,'update_%s_import_dictionary'%(storage_type)):##if you need some more data to import fle from cloud then you will need to define this function _update_{storage_type}_import_dictionary
						response_data = getattr(self,'update_%s_import_dictionary'%(storage_type))(data)
						exported_records[record_folder_id].update(response_data)
			if hasattr(self,'_import_%s_attachment_cloud'%(storage_type)):## need to define this function to import files from cloud _import_{storage_type}_attachment_cloud
				return getattr(self,'_import_%s_attachment_cloud'%(storage_type))(connection,instance_id,storage_type,folder_id,exported_records)
		else:
			message = 'No Records Found In Cloud For Model %s And Ids %s'%(" "\
				.join([i[0].upper() + i[1:] for i in model.split('.')]),record_ids)
		return message_wizard.generate_message(message)
	
	
	@api.model
	def get_fields(self):
		'''
			This function is use to get fields of the cloud_odoo_file_mapping object
		'''
		fields =['record_id','record_folder_name',
		'record_folder_id','record_folder_path',
		'file_url','file_id']
		return fields


	def create_import_attachment(self, record_id, model, data, 
									mime_type, fname, cloud_file_id):
		'''
		This Function use to create attachment in odoo
		@params
		record id:- Ineteger value of record id
		model:- model name like res.partner,sale.order
		mime_type:- mime type of the file
		fname:- File name
		cloud_file_id :- If attachment not to be created in cloud then we will use cloud file id as a storefname
		@returns
		newly create attachment object
		'''
		context = self._context.copy() or {}
		context.update({
		'import_attachment':False,
		'binary_field_real_user': self.env.user
		})
		res_config = self.env['res.config.settings']
		values = res_config.cloud_config_values()
		create_odoo_attachment = values.get('create_odoo_attachment',False)
		self = self.with_context(context)
		ir_attachment = self.env['ir.attachment']
		vals = {
			'res_model':model,
			'res_id':record_id,
			'mimetype':mime_type,
			'name':fname,
			'type':'binary',
			}
		if create_odoo_attachment:
			vals['datas'] = data
		else:
			vals['store_fname'] = cloud_file_id	
		attachment_id = ir_attachment.create([vals])
		return attachment_id
	


	
