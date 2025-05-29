# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import api, fields, models, _
from odoo import SUPERUSER_ID
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	cloud_connection_ids = fields.Many2many(
		'cloud.odoo.connection',
		string = "Cloud Connection",
		help = 'These Connections Will Use To Upload Attachment To Real Time And On Single Export From Record',
		)

	create_odoo_attachment = fields.Boolean(
		string = "Create Odoo Attachment", 
		default = True,
		help = 'This Boolean Field Will Use To Create Attachment In Odoo File Store')
	read_cloud_file = fields.Boolean(
		string = 'Read File From Cloud', 
		default = False,
		help = 'This Boolean Field Will Use To Read File From Cloud')
	export_real_time = fields.Boolean(
		string = 'Export Attachment Real Time', 
		default = False,
		help = 'This Boolean Field Will Use To Export Attachment In Real Time In Cloud')
	export_limit = fields.Integer(
		string='Bulk Export Attachments Limit',
		default=20,
		help = 'The Export Limit Will Use For Bulk Export')

	def set_values(self):
		super(ResConfigSettings, self).set_values()
		ir_values = self.env['ir.default'].sudo()
		connection_ids = self.cloud_connection_ids
		lst = []
		if connection_ids:
			lst = connection_ids.ids
		ir_values.set('res.config.settings', 'create_odoo_attachment', self.create_odoo_attachment)
		ir_values.set('res.config.settings', 'read_cloud_file', self.read_cloud_file)
		ir_values.set('res.config.settings', 'export_real_time', self.export_real_time)
		ir_values.set('res.config.settings', 'export_limit', self.export_limit)
		ir_values.set('res.config.settings', 'cloud_connection_ids',lst)
		return True


	def get_values(self):
		values = super(ResConfigSettings, self).get_values()
		ir_values = self.env['ir.default'].sudo()
		create_odoo_attachment = ir_values._get('res.config.settings', 'create_odoo_attachment')
		read_cloud_file = ir_values._get('res.config.settings', 'read_cloud_file')
		export_real_time = ir_values._get('res.config.settings', 'export_real_time')
		connection_ids = ir_values._get('res.config.settings', 'cloud_connection_ids')
		export_limit = ir_values._get('res.config.settings', 'export_limit')
		if not export_limit:
			export_limit = 20
		if not connection_ids:
			connection_ids = [self.env['cloud.odoo.connection'].search([('active','=',True)],limit=1).id]
			if not connection_ids[0]:
				connection_ids = False
		if not connection_ids:
			create_odoo_attachment = True
		
		values.update({
			'create_odoo_attachment':create_odoo_attachment,
			'export_real_time':export_real_time,
			'read_cloud_file':read_cloud_file,
			'export_limit':export_limit,
			})
		if connection_ids:
			values.update({
			'cloud_connection_ids':[(6,0,(connection_ids))]
			})

		return values
	

	@api.onchange('create_odoo_attachment')
	def onchange_read_file_cloud(self):
		if not self.create_odoo_attachment:
			self.read_cloud_file = True
			self.export_real_time = True
	
	@api.onchange('export_real_time')
	def onchange_export_real_time(self):
		if not self.export_real_time:
			self.create_odoo_attachment = True

	@api.model
	def cloud_config_values(self):
		cloud_odoo_connection = self.env['cloud.odoo.connection']
		ir_values = self.env['ir.default'].sudo()
		values = {}
		create_odoo_attachment = ir_values._get('res.config.settings', 'create_odoo_attachment')
		read_cloud_file = ir_values._get('res.config.settings', 'read_cloud_file')
		export_real_time = ir_values._get('res.config.settings', 'export_real_time')
		connection_ids = ir_values._get('res.config.settings', 'cloud_connection_ids')
		
		if not connection_ids:
			connection_ids = [self.env['cloud.odoo.connection'].search([('active','=',True)],limit=1).id]
		if connection_ids:
			connection_ids = cloud_odoo_connection.browse(connection_ids)
		else:
			connection_ids = []
		if create_odoo_attachment==None:
			create_odoo_attachment = True
		values.update({
			'cloud_connection_ids':connection_ids,
			'create_odoo_attachment':create_odoo_attachment,
			'export_real_time':export_real_time,
			'read_cloud_file':read_cloud_file,
			})
		return values
	
	@api.model
	def cloud_config_limit(self):
		ir_values = self.env['ir.default'].sudo()
		export_limit = ir_values._get('res.config.settings', 'export_limit')
		if not export_limit:
			export_limit = 20
		return export_limit
	
	@api.model
	def set_cloud_config_values(self):
		ir_values = self.env['ir.default'].sudo()
		ir_values.set('res.config.settings', 'create_odoo_attachment', True)
		ir_values.set('res.config.settings', 'read_cloud_file', False)
		ir_values.set('res.config.settings', 'export_real_time', False)
		ir_values.set('res.config.settings', 'export_limit',20)
		return True




