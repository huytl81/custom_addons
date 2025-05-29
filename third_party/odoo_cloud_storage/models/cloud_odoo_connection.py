# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import _, api, fields, models
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

selection_field = [('draft','Draft'),('error','Error'),('done','Done')]


class CloudOdooConnection(models.Model):
	_name = 'cloud.odoo.connection'
	_inherit = ['mail.thread']
	_description = 'Model For Cloud Odoo Connection'

	@api.model
	def _get_storage_types(self):
		storage_type = []
		return storage_type

	name = fields.Char(
		string = 'Storage Name', 
		required=True
		)
	cloud_folder_name =fields.Char(
		string = "Cloud Folder Name",
		required = True)
	cloud_folder_id = fields.Char(
		string = 'Cloud Folder Id',
		)
	cloud_folder_path = fields.Char(
		string = 'Cloud Folder Path'
	)
	active = fields.Boolean(string = 'Active', 
	default = True)
	storage_type = fields.Selection(
		selection='_get_storage_types',
		string="Storage Type",
		required=True)
	connection_status = fields.Boolean(
		string = 'Connection Status',
		default = False
		)
	api_url = fields.Char(
		string= 'Api Url',
		required = True
	)
	color = fields.Char(
		string = 'Color Download',
		required = True,
		help="This color will show on the attachment to download it from cloud"
		)
	color_export = fields.Char(
		string='Color Upload',
		required = True,
		help = "This color will show on the attachment to export it to cloud"
	)
	delete_cloud_attachment = fields.Boolean(
		string = 'Delete Cloud Attachment',
		default = False
	)
	api_key = fields.Char(
		string = 'Api Key',
	required = True
	)
	api_password = fields.Char(
		string = 'Api Password',
		required = True
	)
	model_ids = fields.One2many(
		comodel_name = 'cloud.folder.mapping',
		inverse_name = 'instance_id',
		string = 'Attached Models',
		)
	model_count = fields.Integer(
		string='Model Count',
		compute='_compute_model_count'
	)
	state = fields.Selection(
		selection = selection_field,
		string ="Status",
		default ="draft",
		tracking=True
		)
	message = fields.Text(
		string = "Message",
		tracking=True)
	query_string = fields.Char(
		string = 'Url String'
		)

	@api.model
	def create(self,vals):
		if vals.get('query_string',False):
			res = self.search([('query_string','=',vals['query_string'])])
			if res:
				raise UserError("Query String Already Present In Another Connetion,Please Use Any Unique String")
		return super().create(vals)
	
	@api.depends('model_ids')
	def _compute_model_count(self):
		for record in self:
			record.model_count = len(record.model_ids.ids or [])
	
	@api.onchange('query_string')
	def onchange_api_url(self):
		config_parameter = self.env['ir.config_parameter']
		url = config_parameter.get_param('web.base.url')
		query_string = self.query_string
		if not url.endswith('/'):
			url+= '/'
		url+= 'odoo_cloud_storage/'
		if query_string:
			url+=query_string
		self.api_url = url
	

	def test_connection(self):
		'''
		Test connection between odoo and cloud
		'''
		self.ensure_one()
		if hasattr(self, 'test_%s_connection' % self.storage_type):## need to define this function as test_{storage_type}_connection
			return getattr(self, 'test_%s_connection' % self.storage_type)()
	

	def _track_subtype(self, init_values):
		self.ensure_one()
		if 'message' in init_values:
			return self.env.ref('odoo_cloud_storage.mt_cloud_message') # Full external id
		return super(CloudOdooConnection, self)._track_subtype(init_values)
	
	def unlink(self):
		remove_ids = set(self.ids)
		res = super().unlink()
		if res:
			ir_values = self.env['ir.default'].sudo()
			connection_ids = ir_values._get('res.config.settings', 'cloud_connection_ids')
			if connection_ids:
				lst = list(set(connection_ids)-remove_ids)
				ir_values.set('res.config.settings', 'cloud_connection_ids',lst)
		return res


	@api.model
	def _create_connection(self, instance_id=False, storage_type = False):
		'''
		create connectio between odoo and cloud
		@params:instance_id = id of cloud instance
		@params:storage_type = cloud instance's storage type
		@retuns:require parameters to do operations.
		'''
		ctx = self._context.copy() or {}
		connection = {
			'status': False
			}
		if not instance_id and ctx.get('instance_id',False):
			instance_id = ctx.get('instance_id')
		if instance_id and not storage_type:
			storage_type = self.browse(instance_id).storage_type
		if hasattr(self, '_create_%s_connection' % storage_type):##need to define this function _create_{storage_type}_connection
			connection_data = getattr(self, '_create_%s_connection' % storage_type)(instance_id)
			connection.update(connection_data)
		if not connection['status']:
			message = ''
			if connection.get('error',False):
				message = connection['error']
			raise UserError(
				_('Connection Issue!\Issue While Creating Connection To Cloud:{}'.format(message)))
		return connection
	

	
	def action_open_models(self):
		models = self.model_ids.ids or []
		return {'name': "Attached Folders",
				'view_mode': 'tree,form',
				'view_id': False,
				'res_model': 'cloud.folder.mapping',
				'type': 'ir.actions.act_window',
				'nodestroy': True,
				'target': 'self',
				'domain': [('id', 'in', models)],
				}
	
	def synchronise_folder_data(self):
		"""
		Synchronise Folder To Cloud.
		in you code you can make object of 	cloud.folder.mapping and can call this method

		"""
		self.ensure_one()
		cloud_message = self.env['cloud.message.wizard']
		message = 'Error:Issue in Exporting/Updating Folder'
		instance_id = self
		storage_type = self.storage_type
		state = self.state
		connection = self._create_connection(instance_id.id,storage_type)
		return_data = {}
		folder_id = self.cloud_folder_id
		folder_path = self.cloud_folder_path
		vals ={'folder_name':self.cloud_folder_name} ##Folder name to be created/updated in cloud
		action_funtion = ''
		operation = False
		if state=='done':## if folder already created than need to update folder
			vals.update({
				 'folder_id':folder_id,
				 'folder_path':folder_path
				 })
			action_funtion = "update_%s_folder"%storage_type
		else:
			action_funtion = "create_%s_folder"%storage_type
			operation = True
		if hasattr(self,action_funtion):## define this function to synchronise folder for create(create_test_folder),for update update_test_folder
			return_data = getattr(self,action_funtion)(connection,instance_id,vals)
		if return_data.get('message',False):## return data should have folder_id and folder path and you can returns some extra data but can not returnns extra paramets except message and status
			message = return_data.pop('message')
		if return_data.pop('status',False) and operation:
			return_data['cloud_folder_id'] = return_data.pop('folder_id','')
			return_data['cloud_folder_path'] = return_data.pop('folder_path','')
			return_data['state'] = 'done'  
			self.write(return_data)
		elif self.state!='done':
			self.state = 'error'
		self.message = message
		return cloud_message.generate_message(message)
	

	def action_open_folder_cloud(self):
		storage_type = self.storage_type
		url = False
		cloud_snippet = self.env['cloud.snippet']
		if hasattr(cloud_snippet, 'get_%s_base_url' %storage_type):## If you need some more data to create folder in cloud than you can use this function
			url = getattr(cloud_snippet, 'get_%s_base_url' %storage_type)(self)
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