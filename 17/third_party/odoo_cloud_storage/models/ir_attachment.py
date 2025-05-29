# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models
from odoo.tools import human_size
import base64
import logging
_logger = logging.getLogger(__name__)
connection = False

class IrAttachment(models.Model):
	_inherit = 'ir.attachment'

	@api.depends('store_fname', 'db_datas', 'file_size')
	@api.depends_context('bin_size')
	def _compute_datas(self):
		context = self._context.copy() or {}
		if self._context.get('bin_size'):
			for attach in self:
				context.update({'attachment_id':attach.id})
				attach.datas = human_size(attach.with_context(context).file_size)
			return
		for attach in self:
			context.update({'attachment_id':attach.id})
			attach.datas = base64.b64encode(attach.with_context(context).raw or b'')
	
	
	# def _inverse_datas(self):
	# 	context = self._context.copy() or {}
	# 	for attach in self:
	# 		context.update({'attachment_id':attach.id})
	# 		self = self.with_context(context)
	# 		vals = self._get_datas_related_values(attach.datas, attach.mimetype)
	# 		# take current location in filestore to possibly garbage-collect it
	# 		fname = attach.store_fname
	# 		# write as superuser, as user probably does not have write access
	# 		super(IrAttachment, attach.sudo()).write(vals)
	# 		if fname:
	# 			self._file_delete(fname)

	def _set_attachment_data(self, asbytes):
		context = self._context.copy() or {}
		for attach in self:
			context.update({'attachment_id':attach.id})
			self = self.with_context(context)
			bin_data = asbytes(attach)
			vals = self._get_datas_related_values(bin_data, attach.mimetype)
			fname = attach.store_fname
			super(IrAttachment, attach.sudo()).write(vals)
			if fname:
				self._file_delete(fname)	
	
	# connection = {}
	datas = fields.Binary(string='File Content', compute='_compute_datas', inverse='_inverse_datas')

	@api.model
	def _file_write(self, value, checksum):
		fname,create_odoo_attachment = self.create_cloud_attachment()
		if create_odoo_attachment or create_odoo_attachment==None:
			fname = super()._file_write(value,checksum)		
		return fname

	@api.model
	def create_cloud_attachment(self,attachment_id=False):
		context = self._context.copy() or {}
		if not attachment_id:
			attachment_id = context.get('attachment_id',False)
		values = self.get_values()
		export_real_time = values.get('export_real_time',False)
		create_odoo_attachment = values.get('create_odoo_attachment',True)
		connection_ids = values.get('cloud_connection_ids',[])
		cloud_snippet = self.env['cloud.snippet']
		fname = ''
		if ((context.get('import_attachment',True) and export_real_time) or \
			context.get('export_cloud',False)) and connection_ids and attachment_id:
			cloud_odoo_folder = self.env['cloud.folder.mapping']
			context.update({'from_filestore':False})
			self = self.with_context(context)
			if context.get('export_cloud',False):
				self._cr.commit()
			attachment_obj = self.browse(attachment_id)
			res_model = attachment_obj.res_model
			if res_model and not attachment_obj.res_field:
				check_attach = True
				for connection_id in connection_ids:
					instance_id = connection_id.id
					storage_type = connection_id.storage_type
					domain = [('model_id.model','=',res_model),
					('instance_id','=',instance_id),
					('state','=','done'),
					('is_default','=',True)]
					folder_id = cloud_odoo_folder.search(domain,limit=1)
					if folder_id:
						check_attach = False
						status,connection = self.get_connection(instance_id,storage_type)
						if status:
							connection = connection.get(instance_id)
							status ,message, file_map_id = cloud_snippet.export_attachment_to_cloud(connection,attachment_obj,
							instance_id,storage_type,folder_id)
							if status:
								fname = file_map_id.file_id
								attachment_obj.db_datas = False
							else:
								_logger.info("ERROR 404: File not created on Cloud...%r"%message)
				if check_attach:
					create_odoo_attachment = True
			else:
				create_odoo_attachment = True
		else:
			create_odoo_attachment = True
		return fname,create_odoo_attachment

	@api.model
	def _file_read(self, fname):
		context = self._context.copy() or {}
		context['refresh_token'] = False
		attachment_id = context.get('attachment_id',False)
		values = self.get_values()
		read_cloud_file = values.get('read_cloud_file',False)
		if (context.get('from_filestore',True) and read_cloud_file) or context.get('from_cloud',False): 
			file_env = self.env['cloud.odoo.file.mapping']
			file_map_id = file_env.search([
				('attachment_id','=',attachment_id),
				('instance_id.active','=',True),
				('file_id','not in',[False,''])],
				limit=1)
			self = self.with_context(context)
			cloud_snippet = self.env['cloud.snippet']
			if file_map_id:
				instance_id = file_map_id.instance_id.id
				storage_type = file_map_id.instance_id.storage_type
				status,connection = self.get_connection(instance_id,storage_type)
				if status:
					connection = connection.get(instance_id)
					try:
						if hasattr(cloud_snippet,'read_%s_file'%storage_type):## need to define this file in cloud_snippet read_{storage_type}_file
							response = getattr(cloud_snippet,'read_%s_file'%storage_type)(connection,file_map_id)
						status = response.get('status',False)
						if status:
							r = response.get('content','')
							if r:
								return r
					except Exception as e:
						_logger.info("ERROR 404: File not found on Cloud...%r"%e)
			else:
				read_cloud_file = False
		else:
			read_cloud_file = False
		if not read_cloud_file:
			return super()._file_read(fname)
	
	
	@api.model
	def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
		res = super(IrAttachment,self).search_read(domain, fields, offset, limit, order)
		if fields==['id', 'name', 'mimetype']:
			res_model = [check[2] for check in domain if check and check[0]=='res_model']
			# res = self.update_color(res,res_model)
		return res
	
	def update_color(self,res,res_model):
		if res_model:
			folder_id = self.env['cloud.folder.mapping'].search([('model_id.model','in',res_model)])
			if folder_id:
				file_mapping = self.env['cloud.odoo.file.mapping']
				color_export = self.env['cloud.odoo.connection'].search([],limit=1).mapped('color_export')
				for i in res:
					if i['id']:
						instance_id = file_mapping.search([('attachment_id','=',i['id'])
						,('file_id','not in',['',False])],\
							limit=1).mapped('instance_id')
						if instance_id:
							i['color'] = instance_id.color
							i['exported'] = True
						else:
							i['color'] = color_export
							i['exported'] = False
		return res
	
	def write(self,vals):
		attach_ids = self.ids
		res = super(IrAttachment,self).write(vals)
		if res:
			cloud_odoo_file_ids =  self.env['cloud.odoo.file.mapping'].search([('attachment_id','in',attach_ids)])
			if cloud_odoo_file_ids:
				cloud_odoo_file_ids.state = 'need_sync'
		return res
	
	def unlink(self):
		self.delete_items()
		res = super().unlink()
		return res
	
	def delete_items(self):
		connection_ids = self.env['cloud.odoo.connection'].search([('delete_cloud_attachment','=',True)])
		attach_ids = self.ids
		cloud_odoo_file =  self.env['cloud.odoo.file.mapping']
		cloud_snippet = self.env['cloud.snippet']
		domain = [('attachment_id','in',attach_ids)]
		records =  cloud_odoo_file.search(domain)
		if records:
			for connection_id in connection_ids:
				instance_id = connection_id.id
				storage_type = connection_id.storage_type
				status,connection = self.get_connection(instance_id,storage_type)
				if status:
					connection = connection.get(instance_id)
					file_map_ids = records.filtered(lambda file_map:file_map.instance_id.id==instance_id)
					if hasattr(cloud_snippet,'delete_%s_file'%storage_type):##need to define this function to delete attachment in cloud (delete_{storage_type}_file)
						response = getattr(cloud_snippet,'delete_%s_file'%storage_type)(connection,file_map_ids)
			records.sudo().unlink()
		return True
	
	@api.model
	def create(self,vals):
		context = self._context.copy() or {}
		if 'datas' in vals:
			context['file_data'] = vals['datas']
			self = self.with_context(context)
		attachment_id =  super().create(vals)
		fname,create_odoo_attachment = self.create_cloud_attachment(attachment_id.id)
		if not attachment_id.store_fname:
			attachment_id.store_fname = fname
		return attachment_id

	def get_values(self):
		res_config = self.env['res.config.settings']
		values = res_config.cloud_config_values()
		return values
	

	def get_connection(self, instance_id, storage_type=False):
		global connection
		cloud_odoo_connection = self.env['cloud.odoo.connection']
		status = True
		if getattr(self,'connection',False) and instance_id in getattr(self,'connection',False):
			return status,connection	
		try:
			connection_resp = cloud_odoo_connection._create_connection(instance_id,storage_type)
			if connection_resp.get('status'):
				connection = dict()
				connection[instance_id] = cloud_odoo_connection._create_connection(instance_id,storage_type)
		except Exception as e:
			status = False
		return status,connection
	