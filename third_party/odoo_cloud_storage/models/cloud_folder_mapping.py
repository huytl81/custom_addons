# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

selection_field = [('draft','Draft'),('error','Error'),('done','Done')]

class CloudFolderMapping(models.Model):
	_name = 'cloud.folder.mapping'
	_inherit = "mail.thread"
	_rec_name = 'name'
	_description = 'Model For Cloud Folder With Odoo Models Mapping'

	name = fields.Char(
		string = 'Folder Name',
		required = True
		)
	complete_name = fields.Char(string = 'Folder Name',
	compute='_complete_complete_name', recursive=True)
	folder_path = fields.Char('Folder Path')
	folder_id = fields.Char('Folder Id')
	instance_id = fields.Many2one(
		comodel_name = 'cloud.odoo.connection',
		string = 'Instance Name',
		required = True,
		default = lambda self: self.env['cloud.odoo.connection']\
			.search([('active','=',True)], limit=1).id or False,
		ondelete ='restrict'
		)
	storage_type = fields.Selection(
			related = 'instance_id.storage_type',
			string = 'Storage Type',
			store = True
			)
	parent_id = fields.Many2one(
	'cloud.folder.mapping', 
	string = 'Parent Folder'
	)
	file_ids = fields.One2many(
		comodel_name = 'cloud.odoo.file.mapping',
		inverse_name = 'folder_id',
		string = 'Attached Attachments')
	
	model_id = fields.Many2one('ir.model', string='Model Name', required=True, index=True, ondelete='cascade',
		domain = [('is_mail_thread','=',True)]
	)
	model_name = fields.Char(related = "model_id.model")
	model_domain = fields.Char(
		string = 'Filter Domain', 
		default= []
		)
	file_count = fields.Integer(
		string = 'File Count',
		compute = '_compute_file_count'
	)
	upload_action = fields.Integer(
		string = 'Upload Action',
		default = 0
	)
	download_action = fields.Integer(
		string = 'Download Action',
		default = 0
	)
	run_cron = fields.Boolean(
		string = 'Run Cron',
		default = False
	)
	state = fields.Selection(
		selection = selection_field,
		string ="Status",
		default ="draft",
		tracking = True
		)
	message = fields.Text(
		string = "Message",
		tracking = True
	)
	is_default = fields.Boolean(
		string = 'Is Default',
		default = True,
		help = 'Use this folder to export attachment in real time'
		)

	@api.model
	def create(self,vals):
		if vals.get('model_id',False):
			active_model = self.search([
				('model_id','=',vals['model_id']),
				'|',
				('upload_action','!=',0),
				('download_action','!=',0),],limit=1)
			if active_model:
				if active_model.upload_action:
					vals['upload_action'] = active_model.upload_action
				if active_model.download_action:
					vals['download_action'] = active_model.download_action
			duplicate_model = self.search([
				('model_id','=',vals['model_id']),
				('model_domain','=',vals.get('model_domain',False)),
				('instance_id','=',vals.get('instance_id',False))
			])
			if duplicate_model:
				raise UserError('Folder Already Created With Same Model And Domain')
			if vals.get('is_default',False):
				self_ids = self.search([('model_id','=',vals['model_id'])])
				self_ids.is_default = False
		return super().create(vals)

	
	def write(self, vals):
		if vals.get('model_id', False)\
			 and any(record.file_ids for record in self):
			raise UserError("These Folders{} Have Files Attached"\
				.format([record.name for record in self if record.file_ids]))
		if vals.get('is_default',False):
			instance_ids = self.mapped('instance_id').ids
			domain = [
				('model_id','in',self.mapped('model_id').ids),
				('instance_id','in',instance_ids)
				]
			self_ids = self.search(domain)
			self_ids.is_default = False
		return super().write(vals)
	
	def unlink(self):
		if any(record.file_ids for record in self):
			raise UserError("These Folders{} Have Files Attached"\
				.format([record.name for record in self if record.file_ids]))
		if self.upload_action:
			action_server_export = self.env['ir.actions.server'].browse(self.upload_action)
			action_server_export.unlink()
		if self.download_action:
			action_server_import = self.env['ir.actions.server'].browse(self.download_action)
			action_server_import.unlink()
		res = super().unlink()
		return res


	@api.depends('file_ids')
	def _compute_file_count(self):
		for record in self:
			record.file_count = len(record.file_ids.ids or [])
	
	def _track_subtype(self, init_values):
		self.ensure_one()
		if 'message' in init_values:
			return self.env.ref('odoo_cloud_storage.mt_cloud_folder_message')
		return super(CloudFolderMapping, self)._track_subtype(init_values)


	@api.depends('name', 'parent_id.complete_name','instance_id.cloud_folder_name')
	def _complete_complete_name(self):
		for folder in self:
			parent_folder_name = folder.instance_id.cloud_folder_name
			if folder.parent_id:
				folder.complete_name = '%s / %s' % (folder.parent_id.complete_name, folder.name)
			else:
				folder.complete_name = '%s / %s'%(parent_folder_name,folder.name)
	
	def create_server_action_for_upload(self):
		"""
			Create Server Action To Export Attachment To Cloud.
			in your code you can make object of cloud.folder.mapping(record) and can call this method
		"""
		self.ensure_one()
		model_id = self.model_id.id
		name = self.model_id.name
		already_action = self.search([('model_id','=',model_id),
									('upload_action','!=',0)],limit=1)
		if not already_action:
			message = 'Upload Server Action Created Succesfully For Model %s'%name
			code = "action = env['cloud.synchronization.wizard'].start_cloud_synchronisation(%i,'export')"%model_id
			action_server = False
			try:
				action_server = self.env['ir.actions.server'].create({
					'name':'Export/Update Attachments',
					'model_id': model_id,
					'state':'code',
					'binding_model_id': model_id,
					'code': code
				})
			except Exception as e:
				message= 'Error While Creating Server Action:%s'%str(e)
			if action_server:
				self.upload_action = action_server.id
		else:
			message = 'Upload Server Action Is Already Created For This Model %s'%name
		return self.env['cloud.message.wizard'].generate_message(message)
	
	def create_server_action_for_download(self):
		"""
			Create Server Action To Import Attachment.
			in you code you can make object of 	cloud.folder.mapping and can call this method
		"""
		
		self.ensure_one()
		model_id = self.model_id.id
		name = self.model_id.name
		already_action = self.search([('model_id','=',model_id),
									('download_action','!=',0)],limit=1)
		if not already_action:
			message = 'Download Server Action Created Succesfully For Model %s'%name
			code = "action = env['cloud.synchronization.wizard'].start_cloud_synchronisation(%i,'import')"%model_id
			action_server = False
			try:
				action_server = self.env['ir.actions.server'].create({
					'name':'Import Attachments',
					'model_id': model_id,
					'state':'code',
					'binding_model_id': model_id,
					'code': code
				})
			except Exception as e:
				message= 'Error While Creating Server Action:%s'%str(e)
			if action_server:
				self.download_action = action_server.id
		else:
			message = 'Download Server Action Is Already Created For This Model %s'%name
		return self.env['cloud.message.wizard'].generate_message(message)

	
	def synchronise_folder_data(self):
		"""
		Synchronise Folder To Cloud.
		in you code you can make object of 	cloud.folder.mapping and can call this method

		"""
		self.ensure_one()
		cloud_snippet = self.env['cloud.snippet'].browse([])
		cloud_connection = self.env['cloud.odoo.connection']
		cloud_message = self.env['cloud.message.wizard']
		message = 'Error:Issue in Exporting/Updating Folder'
		instance_id = self.instance_id
		storage_type = self.storage_type
		state = self.state
		connection = cloud_connection._create_connection(instance_id.id,storage_type)
		return_data = {}
		folder_id = self.folder_id
		folder_path = self.folder_path
		vals ={'folder_name':self.name} ##Folder name to be created/updated in cloud
		action_funtion = ''
		operation = False
		if state =='done':## if folder already created than need to update folder
			vals.update({
				 'folder_id':folder_id,
				 'folder_path':folder_path
				 })
			action_funtion = "update_%s_folder"%storage_type
		else:
			parent_folder_id = self.parent_id.folder_id or instance_id.cloud_folder_id or ''
			parent_folder_path =  self.parent_id.folder_path or instance_id.cloud_folder_path or ''
			vals.update({
					'parent_folder_id': parent_folder_id,
					'parent_folder_path':parent_folder_path
					})
			action_funtion = "create_%s_folder"%storage_type
			operation = True
		if hasattr(self, 'get_%s_folder_data' %storage_type):## If you need some more data to create folder in cloud than you can use this function
			updated_vals = getattr(self, 'get_%s_folder_data' %storage_type)()
			vals.update(updated_vals)
		if hasattr(cloud_snippet,action_funtion):## define this function to synchronise folder for create(create_test_folder),for update update_test_folder
			return_data = getattr(cloud_snippet,action_funtion)(connection,instance_id,vals)## return data should not have extra parameters except status and message. because this will write to the object and needs exact same fields
		if return_data.get('message',False):
			message = return_data.pop('message')
		if return_data.pop('status',False) and operation:
			return_data['state'] = 'done'  
			self.write(return_data)
		elif self.state!='done':
			self.state = 'error'
		self.message = message ## message will print on the record's footer 
		return cloud_message.generate_message(message)
	
	def synchronise_folder_files(self):
		'''To Export Attachment of the folder 
		you will have to call this method by this model's object'''
		self.ensure_one()
		cloud_snippet = self.env['cloud.snippet']
		cloud_message = self.env['cloud.message.wizard']
		cloud_odoo_connection = self.env['cloud.odoo.connection']
		model = self.model_id.model
		domain = safe_eval(self.model_domain)
		folder_id = self
		instance_id = self.instance_id.id
		storage_type = self.instance_id.storage_type
		connection = cloud_odoo_connection._create_connection(instance_id,storage_type)
		active_ids =self.env[model].search(domain).ids
		if not active_ids:
			return cloud_message.generate_message('No Active Records Find For The Given Domain')
		return cloud_snippet.sync_attachment_cloud(connection,model,active_ids,folder_id,
													instance_id,storage_type)
	

	def download_folder_files(self):
		'''To Import Attachments of the folder 
		you will have to call this method by this model's object'''
		self.ensure_one()
		cloud_snippet = self.env['cloud.snippet']
		cloud_message = self.env['cloud.message.wizard']
		cloud_odoo_connection = self.env['cloud.odoo.connection']
		model = self.model_id.model
		domain = safe_eval(self.model_domain)
		folder_id = self
		instance_id = self.instance_id.id
		storage_type = self.instance_id.storage_type
		connection = cloud_odoo_connection._create_connection(instance_id,storage_type)
		active_ids =self.env[model].search(domain).ids
		if not active_ids:
			return cloud_message.generate_message('No Active Records Find For The Given Domain')
		return cloud_snippet.import_attachment_cloud(connection,model,active_ids,
				instance_id,storage_type,folder_id.id)
		


	def action_open_folder_cloud(self):
		instance_obj = self.instance_id
		storage_type = instance_obj.storage_type
		url = False
		cloud_snippet = self.env['cloud.snippet']
		if hasattr(cloud_snippet, 'get_%s_folder_url' %storage_type):## If you need some more data to create folder in cloud than you can use this function
			url = getattr(cloud_snippet, 'get_%s_folder_url' %storage_type)(self)
		if url:
			return {
				'name': 'Go to SkyDrive',
				'res_model': 'ir.actions.act_url',
				'type'     : 'ir.actions.act_url',
				'target'   : 'new',
				'url'      : url
			   }
		else:
			raise UserError("Not Able To Open Folder In Cloud")


	def action_open_files(self):
		files = self.file_ids.ids or []
		return {'name': "Attach Files",
				'view_mode': 'tree,form',
				'view_id': False,
				'res_model': 'cloud.odoo.file.mapping',
				'type': 'ir.actions.act_window',
				'nodestroy': True,
				'target': 'self',
				'domain': [('id', 'in', files)],
				}

	

	
			
