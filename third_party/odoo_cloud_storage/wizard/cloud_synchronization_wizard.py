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

connection  = 'cloud.odoo.connection'


class CloudSynchronizationWizard(models.TransientModel):
	_name = 'cloud.synchronization.wizard'
	_description = "Cloud Synchronization Wizard"

	def _default_instance_name(self):
		return self.env[connection].search([], limit=1).id

	action = fields.Selection(
		selection =[('import', 'Import File'), ('export', 'Export File')], 
		string='Action', 
		default="export", 
		required=True,
		help="""Import File: Import Files From Cloud. Export File:Export File To Cloud""")
	instance_id = fields.Many2one(
		comodel_name = connection, 
		string='Cloud Instance', 
		default=lambda self: self._default_instance_name())
	model_id = fields.Many2one(
		comodel_name ='ir.model',
		string = 'Model Name',
		readonly = True
	)
	folder_id = fields.Many2one(
		comodel_name = 'cloud.folder.mapping',
		string = 'Select Folder'
		)
	instance_count = fields.Integer(
		string = 'Instance Count',
		default = lambda self: len(self.env[connection].search([('active','=',True)]).ids) or 0
	)
	folder_count = fields.Integer(
		string = 'Folder Count',
		compute = '_compute_file_count'
	)

	def start_action_cloud_synchronization(self):
		context = self._context.copy() or {}
		action = self.action
		active_ids = context.get('active_ids',False)
		model = self.model_id.model
		storage_type = self.instance_id.storage_type
		instance_id = self.instance_id.id
		folder_id = self.folder_id
		if not folder_id:
			raise UserError('No Mapped Folder Found With Active Model And Connection')
		cloud_snippet = self.env['cloud.snippet']
		connection = self.env['cloud.odoo.connection']._create_connection(instance_id,storage_type)
		if active_ids:
			if action == 'export':
				return cloud_snippet.sync_attachment_cloud(connection,model,active_ids,folder_id,
													instance_id,storage_type)
			else:
				return cloud_snippet.import_attachment_cloud(connection,model,active_ids,
				instance_id,storage_type,folder_id.id) 
		else:
			raise UserError('Please Select Any Record')

	@api.depends('model_id')
	def _compute_file_count(self):
		for record in self:
			folder_ids = self.env['cloud.folder.mapping'].search([('model_id','=',record.model_id.id),
												('instance_id','=',record.instance_id.id)])
			if folder_ids:
				folder_len = len(folder_ids.ids)
			else:
				folder_len = 0
			record.folder_count = folder_len
	
	@api.onchange('instance_id')
	def _onchange_folder_id(self):
		self.folder_id = self.env['cloud.folder.mapping'].search(\
			[('model_id','=',self.model_id.id),('instance_id','=',self.instance_id.id)],limit =1).id or False
			
	def start_cloud_synchronisation(self,model_id, action):
		vals = dict()
		vals['model_id']= model_id
		vals['action'] = action
		partial_id = self.create(vals)
		ctx = dict(self._context or {})
		ctx['server_action'] = False
		if partial_id.instance_count>1 or partial_id.folder_count>1:
			self.set_folder(partial_id, model_id)
			return {'name': "Synchronization Attachment",
					'view_mode': 'form',
					'view_id': False,
					'res_model': 'cloud.synchronization.wizard',
					'res_id': partial_id.id,
					'type': 'ir.actions.act_window',
					'nodestroy': True,
					'target': 'new',
					'context': ctx,
					'domain': '[]',
			}
		else:
			self.set_folder(partial_id,model_id)
			return partial_id.start_action_cloud_synchronization()

	def set_folder(self , partial_id, model_id):
		folder_id = self.env['cloud.folder.mapping'].search([('model_id','=',model_id),
			('instance_id','=',partial_id.instance_id.id)],limit =1)
		if folder_id:
			partial_id.folder_id = folder_id.id