# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   "License URL : <https://store.webkul.com/license.html/>"
#
##########################################################################

import logging
from odoo import http
from odoo.http import Response
import base64
from odoo.http import request
from odoo.addons.web.controllers.binary import Binary
_logger = logging.getLogger(__name__)


class CloudStorageMain(http.Controller):

	@http.route('/odoo_cloud_storage/<string:query_string>',type='http',auth='user')
	def odoo_cloud_storage(self, query_string, *args,**kwargs):
		cloud_connection = request.env['cloud.odoo.connection']
		try:
			response = cloud_connection.search([('query_string','=',query_string)],limit =1)
			if response:
				storage_type = response.storage_type
				if hasattr(cloud_connection,'_create_%s_flow'%storage_type):
					get = getattr(cloud_connection,'_create_%s_flow'%storage_type)(response.id, *args, **kwargs)
			action_id = request.env.ref('odoo_cloud_storage.cloud_odoo_connection_mapping').id
			url = "/web#id={}&action={}&model=cloud.odoo.connection&view_type=form".format(response.id,action_id)
			return request.redirect(url)
		except Exception as e:
			_logger.error("=========Error Found While Generating Access Token==================================%r",str(e))
	

	@http.route('/odoo_cloud_storage/open_folder/<string:model>/<int:res_id>',type='json',auth='user')
	def open_folder(self, model, res_id):
		url = ''
		status = False
		map_id = True
		try:
			domain = [('record_id','=',res_id),
			('folder_id.model_id.model','=',model),
			('state','in',['done','need_sync'])]
			file_map_id = request.env['cloud.odoo.file.mapping'].search(domain, limit=1)
			if file_map_id:
				instance_id = file_map_id.instance_id
				storage_type = instance_id.storage_type
				cloud_cnippet = request.env['cloud.snippet']
				if hasattr(cloud_cnippet,'get_%s_file_url'%storage_type):
					url = getattr(cloud_cnippet,'get_%s_file_url'%storage_type)(file_map_id,instance_id)
				if url:
					status = True
			else:
				map_id = False		
		except Exception as e:
			pass
		return{
			'status':status,
			'url':url,
			'map_id':map_id
		}	

	@http.route('/odoo_cloud_storage/action_attachment_cloud/export',type='json',auth='user')
	def action_attachment_cloud(self,attachment_id=False):
		fname = ''
		status = False
		if attachment_id:
			fname,create_odoo_attachment = request.env['ir.attachment'].\
					with_context(export_cloud=True).create_cloud_attachment(int(attachment_id))
		if fname:
			status = True
		return status


	@http.route('/odoo_cloud_storage/get_models', type='json', auth='user')
	def get_models(self):
		models = request.env['cloud.folder.mapping'].search([]).mapped('model_id.model')
		if type(models)!=list:
			models = [models]
		return models
	
	
	@http.route('/odoo_cloud_storage/fetch_folder_extra_data',type='json',auth='user')
	def fetch_folder_extra_data(self):
		folder_data = request.env['cloud.folder.mapping'].search([])
		data = {}
		for folder in folder_data:
			data.update({folder.id:{'name':folder.name,
									'file_count':folder.file_count,'date':folder.create_date,
									'state':folder.state
			}})
		return data
	
	@http.route('/odoo_cloud_storage/fetch_attachment_data',type='json',auth='user')
	def fetch_attachment_data(self):
		def change_mb_to_gb(mb):
			Gb = 1024
			if mb>Gb:
				return float('{0:.2f}'.format(mb/1024)),'GB'
			return float('{0:.2f}'.format(mb)), 'MB'
		select_sql_clause = """SELECT SUM(file_size) as size_total,count(file_type) as count_files,
		file_type 
		FROM cloud_odoo_file_mapping group by file_type order by file_type asc"""
		request.env.cr.execute(select_sql_clause)
		query_results = request.env.cr.dictfetchall()
		counts = {'total_sum':0,'file_data':{},'html':''}
		total_sum = 0.0
		html = ''
		color = {'image':'#9954F2','other':'#F88F43','pdf':'#1AC0D7','text':'#2ADF7D','js':'#FFFFFF'}
		for query in query_results: 
			query['file_type'] = '' if query.get('file_type') is None else query.get('file_type', '')
			query['size_total'] = 0 if query.get('size_total') is None else query.get('size_total', 0)
			total_sum+= query['size_total']
			counts['file_data'].update({
				query['file_type'].upper():
				{'total_size':'%s%s'%change_mb_to_gb(query['size_total']),
				'total_files':query['count_files'],
				'img_url':'/odoo_cloud_storage/static/src/img/%s.png'%query['file_type']}
				})
		for query in query_results:
			html = self.calculate_graph_html(total_sum,query['size_total'],html,color.get(query['file_type'],'blue'))
		counts['html'] = html
		total_size, data_type = change_mb_to_gb(total_sum)
		counts['total_sum'] = '%s%s'%(total_size,data_type)
		counts['data_type']= data_type
		return counts
	
	def calculate_graph_html(self,total_sum,size_total,html,color):
		try:
			size_perc = round((size_total*100)/total_sum,0)
		except ZeroDivisionError as e:
			pass
			size_perc = 0
		html+= '''
			<span style="background-color: {};flex: 0 0 {}%;height:10px;"></span>
		'''.format(color,size_perc)
		return html

	@http.route('/odoo_cloud_storage/fetch_folder_data',type='json',auth='user')
	def fetch_folder_data(self, statuses = []):
		if not statuses:
			string_for_query = "('')"
		else:
			string_for_query = '('
			for status in statuses:
				string_for_query+= "'"+status+"',"
			string_for_query = string_for_query[0:-1]+ ')'
		color = {'draft':'#FFA775',
		'error':'#5665EF',
		'done':'#56D3EF'}
		select_sql_clause = """SELECT count(state) as total_state,
		state 
		FROM cloud_folder_mapping where state not in %s group by state"""%string_for_query
		request.env.cr.execute(select_sql_clause)
		query_results = request.env.cr.dictfetchall()
		data = {'folder_data':{},'folder_statuses':{},'total_sum':0,'color':[]}
		t_sum = 0
		for check in query_results:
			data['folder_data'][check['state']] = check['total_state']
			t_sum+= check['total_state']
			data['color'].append(color.get(check['state'],'red'))
			data['folder_statuses'][check['state']] = check['state'].upper()
		data['total_sum'] = t_sum
		return data

	@http.route('/odoo_cloud_storage/fetch_file_data',type='json',auth='user')
	def fetch_file_data(self, statuses = []):
		if not statuses:
			string_for_query = "('')"
		else:
			string_for_query = '('
			for status in statuses:
				string_for_query+= "'"+status+"',"
			string_for_query = string_for_query[0:-1]+ ')'
		color = {'draft':'#FFA775',
		'error':'#5665EF',
		'need_sync':'#FFA397',
		'done':'#56D3EF'}
		select_sql_clause = """SELECT count(state) as total_state,
		state 
		FROM cloud_odoo_file_mapping where state not in %s group by state"""%string_for_query
		
		request.env.cr.execute(select_sql_clause)
		query_results = request.env.cr.dictfetchall()
		data = {'file_data':{},'file_statuses':{},'total_sum':0,'color':[]}
		t_sum = 0
		for check in query_results:
			data['file_data'][check['state']] = check['total_state']
			t_sum+= check['total_state']
			data['color'].append(color.get(check['state'],'red'))
			data['file_statuses'][check['state']] = check['state'].upper()
		data['total_sum'] = t_sum
		return data
		
	@http.route('/odoo_cloud_storage/get_action',type='json',auth='user')
	def get_action(self, action=None):
		env = request.env
		res_id = False
		res_model = False
		if action == 'add':
			res_model = 'cloud.odoo.connection'
		else:
			res_model = 'cloud.bulk.synchronisation'
			if action =='export':
				res_id = env[res_model].create({
					'action':'export'}).id
			else:
				res_id = env[res_model].create({
					'action':'import'}).id
		return{
			'id':res_id,
			'model':res_model
		}

	@http.route('/odoo_cloud_storage/fetch_connection_data', type='json', auth='user')
	def fetch_connection_data(self):
		connection_env = request.env['cloud.odoo.connection']
		data = connection_env.search_read([],['name','id','storage_type'])
		for row in data:
			folder_count = request.env['cloud.folder.mapping'].search_count([('instance_id','=',row['id'])])
			file_count = request.env['cloud.odoo.file.mapping'].search_count([('instance_id','=',row['id'])])
			if hasattr(connection_env,'get_dashboard_%s_data'%row['storage_type']):
				row = getattr(connection_env,'get_dashboard_%s_data'%row['storage_type'])(row)
			row['name'] = " ".join(row['name'].split(' ')[:2])
			row.update({
			'folder_count':folder_count,
			'file_count':file_count
			})
		return data


class WebMain(Binary):
	
	@http.route([], type='http', auth="public")
	def content_common(self, xmlid=None, model='ir.attachment', id=None, field='datas',
					   filename=None, filename_field='name', unique=None, mimetype=None,
					   download=None, data=None, token=None, access_token=None, **kw):
		if kw.get('from_cloud',False):
			request.env.context = dict(request.env.context, from_cloud = True)
		else:
			request.env.context = dict(request.env.context, from_filestore=False)
		return super(WebMain,self).content_common(xmlid, model, id, field,
					   filename, filename_field, unique, mimetype,
					   download, data, token, access_token, **kw)
