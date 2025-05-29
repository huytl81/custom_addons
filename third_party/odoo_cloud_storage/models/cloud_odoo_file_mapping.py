# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

selection_field = [('draft','Draft'),
					('error','Error'),
					('need_sync','Update'),
					('done','Done')]

class CloudOdooFileMapping(models.Model):
	_name = 'cloud.odoo.file.mapping'
	_inherit = ["mail.thread","mail.activity.mixin"]
	_rec_name = 'attachment_id'
	_description = 'Model For Cloud Odoo File Mapping'
	
	record_id = fields.Integer(
		string = 'Record Id'
		)
	record_folder_name = fields.Char(
		'Record Folder Name'
	)
	record_folder_id = fields.Char(
		'Record Folder Id'
	)
	record_folder_path = fields.Char(
		'Record Folder Path'
	)
	file_url = fields.Char(string= 'File Url')
	file_id = fields.Char(string=' File Id')
	folder_id = fields.Many2one(
		comodel_name = 'cloud.folder.mapping',
		string = 'Folder Name',
	)
	instance_id = fields.Many2one(
		comodel_name = 'cloud.odoo.connection',
		string = 'Instance Name',
		required = True,
		default = lambda self: self.env['cloud.odoo.connection']\
			.search([('active','=',True)], limit=1).id or False
		)
	
	storage_type = fields.Selection(
			related = 'instance_id.storage_type',
			string = 'Storage Type',
			store = True,
			)
	
	state = fields.Selection(selection = selection_field,
	string = 'Status',
	default='draft',
	tracking = 2)
	
	attachment_id = fields.Many2one(
		comodel_name = 'ir.attachment',
		string = 'Attachment'
		)
	file_size = fields.Float(
		string = 'File Size in Mb',
		compute ='_compute_file_size_type',
		store = True,
		readonly = True
	)

	file_type = fields.Selection(
		string = 'File Type',
		selection = [('js', 'JS'), 
		('image', 'IMAGE'),
		('other','OTHER'),('pdf','PDF'),
		('text','Text')],
		compute = '_compute_file_size_type',
		store = True,
		readonly = True
	)

	attachment_name = fields.Char(
		'Attachment Name',
		tracking=1)
	
	message = fields.Text(
		string = "Message",
		tracking=1)
	

	@api.depends('attachment_id','attachment_id.name')
	def _compute_file_size_type(self):
		def get_file_type(mime_type):
			if mime_type=='application/javascript':
				return 'js'
			elif  mime_type=='image/png' or mime_type=='image/jpeg':
				return 'image'
			elif mime_type=='application/pdf':
				return 'pdf'
			elif mime_type=='text/plain':
				return 'text'
			else:
				return 'other'
		for record in self:
			attachment_id = record.attachment_id
			if attachment_id:
				file_size = attachment_id.file_size
				MB = 1024**2
				record.update({
					'file_size':float('{0:.2f}'.format(file_size/MB)),
					'file_type':get_file_type(attachment_id.mimetype),
					'attachment_name':attachment_id.name
					})
	
	def _track_subtype(self, init_values):
		self.ensure_one()
		if 'message' in init_values:
			return self.env.ref('odoo_cloud_storage.mt_cloud_file_message') # Full external id
		return super(CloudOdooFileMapping,self)._track_subtype(init_values)


	def synchronise_file_data(self):
		'''
		Synchronise file records containng state 'error' to cloud

		'''
		objs = self.filtered(lambda obj: obj.state == 'error')
		successfull_ids = []
		unsuccessfull_ids = []
		cloud_snippet = self.env['cloud.snippet']
		cloud_connection = self.env['cloud.odoo.connection']
		message_wizard = self.env['cloud.message.wizard']
		for record in objs:
			folder_id = self.folder_id
			attachmentObj = self.attachment_id
			instance_id = self.instance_id.id
			storage_type = self.storage_type
			connection = cloud_connection._create_connection(instance_id,storage_type)
			status, message, file_map_id = cloud_snippet.export_attachment_to_cloud(connection,attachmentObj,instance_id,storage_type,folder_id)
			if status:
				successfull_ids.append(attachmentObj.id)
			else:
				unsuccessfull_ids.append(message)
		if successfull_ids and not unsuccessfull_ids:
			printmessage = 'Successfull Synchronise Ids Are:{}'.format(successfull_ids)
		elif unsuccessfull_ids and not successfull_ids:
			printmessage = 'UnsuccessFull Synchronise Message:{}'.format(unsuccessfull_ids)
		else:
			printmessage = 'Successfull Synchronise Ids Are:{}'.format(successfull_ids) + \
				' And UnsuccessFull Synchronise Ids With Message:{}'.format(unsuccessfull_ids)
		return message_wizard.generate_message(printmessage)
	
	# def give_permission(self):
	# 	cloud_connection = self.env['cloud.odoo.connection']
	# 	file_id = self.file_id
	# 	instance_id = self.instance_id.id
	# 	storage_type = self.storage_type
	# 	connection = cloud_connection._create_connection(instance_id,storage_type)
	# 	url = connection.get('url',False)
	# 	perm_url = url + '/me/drive/items/878DD2D6F99B3499!2395/invite'
	# 	skydrive = connection.get('skydrive',False)
	# 	access_token = connection.get('access_token',False)
	# 	headers = {
	# 		'Authorization': 'bearer {}'.format(access_token),
	# 		'Content-type': 'application/json'
	# 		}
	# 	data = 	{
	# 		"recipients": [
	# 			{
	# 			"email": "ratedrjangid@gmail.com"
	# 			}
	# 		],
	# 		"message": "Here's the file that we are going to give you permission.",
	# 		"requireSignIn": False,
	# 		"sendInvitation": True,
	# 		"roles": ["write"]
	# 	}
	# 	import json
	# 	json_data = json.dumps(data)
	# 	try:
	# 		response = skydrive.call_drive_api(perm_url,'POST',data=json_data, headers=headers)
	# 		_logger.info("===================================%r",response)
	# 	except Exception as e:
	# 		_logger.info("===================================%r",e)
	# 	return True




