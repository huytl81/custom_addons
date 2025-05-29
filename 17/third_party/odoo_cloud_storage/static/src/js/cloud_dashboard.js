/** @odoo-module */
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL: <https://store.webkul.com/license.html/> */

import { registry } from "@web/core/registry";
import { loadBundle } from "@web/core/assets";
const { useRef, Component, onPatched, onMounted, useState, onWillStart } = owl;
import { useService } from "@web/core/utils/hooks";

export class CloudDashboard extends Component{

	setup() {
		this.rpc = useService("rpc")
		this.action = useService("action")
		onWillStart(() => {
			loadBundle({
			jsLibs: [
				'/web/static/lib/Chart/Chart.js',
			]
		  })
		  let self = this;
			self.folder_neglet_status = [];
			self.file_neglet_status = [];
			return $.when(
				// ajax.loadLibs(this),
				// this._super(),
			).then(function () {
				return self.fetch_folder_data()
			}).then(function () {
				return self.fetch_file_data()
			}).then(function(){
				return self.fetch_connection_data()
			}).then(function(){
				return self.fetch_folder_extra_data()
			}).then(function(){
				return self.fetch_attachment_data()
			})
		});
		onMounted(() => {
			// do something here
			this.on_attach_callback();
		});
	}

	_uploadAtatchmentToCloud(ev) {
		varattachment_id = $(ev.currentTarget).data('id');
		jsonrpc('/odoo_cloud_storage/action_attachment_cloud/export',
			{ "attachment_id": attachment_id }).then(function (res) {
				if (res) {
					alert("Attachment Successfully Exported To Cloud");
				}
				else {
					alert('Attachment Not Exported Succesfully To Cloud');
				}
			}
		);
	}

	change_file_graph(ev){
		var self = this;
		var status = ev.currentTarget.id;
		if(!self.file_neglet_status.includes(status)){
			self.file_neglet_status.push(status);
			$(ev.currentTarget).css('textDecoration','line-through');
						
		}
		else{
			const index = self.file_neglet_status.indexOf(status);
			if (index > -1) {
				self.file_neglet_status.splice(index, 1);
			}
			$(ev.currentTarget).css('textDecoration','none');
		}
		return $.when().then(function(){
					return self.fetch_file_data()
				}).then(function(){
					return self._chartRegistry()
			}).then(function(){
				return self.render_file_doughnut_graph()
		})
	}

	change_folder_graph(ev){
		var self = this;
		var status = ev.currentTarget.id;
		if(!self.folder_neglet_status.includes(status)){
			self.folder_neglet_status.push(status);	
			$(ev.currentTarget).css('textDecoration','line-through');
		}
		else{
			const index = self.folder_neglet_status.indexOf(status);
			if (index > -1) {
				self.folder_neglet_status.splice(index, 1);
			}
			$(ev.currentTarget).css('textDecoration','none');
		}
		return $.when().then(function(){
					return self.fetch_folder_data()
				}).then(function(){
					return self._chartRegistry()
			}).then(function(){
				return self.render_folder_doughnut_graph()
		})
	}
	fetch_folder_extra_data () {
		let self = this;
		return this.rpc('/odoo_cloud_storage/fetch_folder_extra_data',).then(function (result) {
				self.folder_extra_data = result
		})
	}
	fetch_attachment_data () {
		let self = this;
		return this.rpc('/odoo_cloud_storage/fetch_attachment_data',).then(function (result) {
			console.log('result.file_data')
			console.log(result.file_data)
			self.attachment_data = result.file_data
			self.total_attachment_sum = result.total_sum
			self.graph_html = result.html
			self.data_type = result.data_type
		})
	}

	on_attach_callback () {
		// this._chartRegistry();
		this.render_folder_doughnut_graph()
		this.render_file_doughnut_graph()
		this.render_bar_graph()
	}
	fetch_connection_data () {
		let self = this;
		return this.rpc('/odoo_cloud_storage/fetch_connection_data',).then(function (result) {
			self.connection_data = result
		})
	}

	call_cloud_action(name, res_model, domain, view_type, res_id=false,nodestroy=false,target='self'){
		let self = this;
		return this.action.doAction({
			name: name,
			type: 'ir.actions.act_window',
			res_model: res_model,
			views: view_type,
			domain:domain,
			res_id:res_id,
			nodestroy: nodestroy,
			target: target,	
		});
	}
	open_connection_view(ev){
		var action_id = parseInt(ev.currentTarget.dataset['id']);
		var text = $(ev.target).text();
		var model = 'cloud.odoo.connection';
		var domain = [];
		let self = this;
		var view_type = [[false,'form'],[false,'tree']];
		var name = 'Cloud Connection';
		if(text=='Folders'){
			name = 'Cloud Folder';
			model= 'cloud.folder.mapping'
			domain = [['instance_id','=',action_id]]
			view_type = [[false,'list'],[false,'form']];
			action_id = false;
		}
		else if(text=='Files'){
			name = 'Cloud File'
			model = 'cloud.odoo.file.mapping'
			domain = [['instance_id','=',action_id]]
			view_type = [[false,'list'],[false,'form']];
			action_id = false;
		}
		return self.call_cloud_action(name, model, domain, view_type,action_id);

	}
	open_list_view(ev){
		var action_id = ev.currentTarget.id;
		let self = this;
		var domain = [];
		var view_type = [[false,'list'],[false,'form']];
		var model = false;
		var name = 'Cloud Odoo Connection';
		if(action_id=='connection')
			model = 'cloud.odoo.connection'
		else if(action_id=='folder'){
			model= 'cloud.folder.mapping'
			name = 'Cloud Folder Mapping';
		}
		return self.call_cloud_action(name, model, domain, view_type);
	}
	open_form_connection(ev){
		var action_id = parseInt(ev.currentTarget.dataset['id']);
		let self = this;
		var domain = [];
		var view_type = [[false,'form'],[false,'list']];
		var model = 'cloud.odoo.connection';
		return self.call_cloud_action('Cloud Connection', model, domain, view_type,action_id);

	}
	open_form_folder(ev){
		var action_id = parseInt(ev.currentTarget.dataset['id']);
		let self = this;
		var domain = [];
		var view_type = [[false,'form'],[false,'list']];
		var model = 'cloud.folder.mapping';
		return self.call_cloud_action('Cloud Folder', model, domain, view_type,action_id);
	}
	on_open_wizard(ev){
		var action_id = ev.currentTarget.id;
		let self = this;
		return this.rpc('/odoo_cloud_storage/get_action',{action:action_id}).then(function(result){
			var id = result.id;
			var domain = [];
			var view_type = [[false,'form'],[false,'list']];
			var nodestroy = false;
			var target = 'self';
			var name = 'Cloud Connection';
			if(id){
				domain = []
				name = 'Bulk Synchronisation';
				nodestroy = true;
				target ='new';
				view_type = [[false,'form']];
			}	
			var model = result.model;
			return self.call_cloud_action(name, model, domain, view_type, id,nodestroy,target);
		})
	}
	fetch_folder_data () {
		let self = this
		return this.rpc('/odoo_cloud_storage/fetch_folder_data', {'statuses':self.folder_neglet_status}).then(function (result) {
			self.folder_data = result.folder_data
			self.folder_statuses = result.folder_statuses
			self.total_folder_sum = result.total_sum.toString().concat(' Folders')
			self.folder_colors = result.color
		})
	}
	fetch_file_data () {
		let self = this
		console.log(self.file_neglet_status)
		return this.rpc('/odoo_cloud_storage/fetch_file_data',{'statuses':self.file_neglet_status}).then(function (result) {
			self.file_data = result.file_data
			self.file_statuses = result.file_statuses
			self.total_file_sum = result.total_sum.toString().concat(' Files')
			self.file_colors = result.color
		})
	}
	_chartRegistry () {
		Chart.register({
		  beforeDraw: function (chart) {
					  // use to add center text in doughnut chart
			if (chart.config.options.elements.center) {
			  var ctx = chart.chart.ctx;
			  var centerConfig = chart.config.options.elements.center;
			  var txt = centerConfig.text;
			  var color = '#555555';
			  var sidePadding = centerConfig.sidePadding || 30;
			  var sidePaddingCalculated = (sidePadding/100) * (chart.innerRadius * 2);
			  ctx.font = "20px Montserrat";
			  var stringWidth = ctx.measureText(txt).width;
			  var elementWidth = (chart.innerRadius * 2) - sidePaddingCalculated;
			  var widthRatio = elementWidth / stringWidth;
			  var newFontSize = Math.floor(30 * widthRatio);
			  var elementHeight = (chart.innerRadius * 2);
			  var fontSizeToUse = Math.min(newFontSize, elementHeight);
			  ctx.textAlign = 'center';
			  ctx.textBaseline = 'middle';
			  ctx.overflow = 'hidden';
			  var centerX = ((chart.chartArea.left + chart.chartArea.right) / 2);
			  var centerY = ((chart.chartArea.top + chart.chartArea.bottom) / 2);
			  ctx.fillStyle = color;
			  ctx.shadowColor = '#FFFFFF';
			  ctx.shadowBlur = 25;
			  ctx.shadowOffsetX = 2;
			  ctx.shadowOffsetY = 2;
			  ctx.fillText(txt, centerX, centerY);
			}
		  },
		});
	  }
	render_bar_graph () {
		if(this.graph_html)
			$('#bar_graph').empty().append(this.graph_html);
		return true;
	}

	
	render_folder_doughnut_graph () {
		let self = this;
		console.log("self")
		$('#cloud_dashboard_folder').replaceWith($('<canvas/>',{id:'cloud_dashboard_folder'}))
		var chart = new Chart('cloud_dashboard_folder',{
			type: 'doughnut',
			data: {
				labels: Object.keys(self.folder_data),
				datasets: [{
					data: Object.values(self.folder_data),
					backgroundColor:self.folder_colors
				}],
			},
			options: {
				responsive: true,
				cutout: "70%",
				maintainAspectRatio: false,
				aspectRatio: 1.7,
				plugins: {
					legend: {
						display:true,
						position: 'bottom',
					},
					title: {
                        display: true,
                        text: self.total_folder_sum,
                        padding: 2,
						position: 'top',
                    },
				},

				cutoutPercentage:80,
				elements:{
					center: {
						text: self.total_folder_sum,
					}
				},
				onClick (e,i){
					if (i.length) {
						var state = chart.data.labels[i[0].index]
						// var state = i[0]['_view']['label']
						state =  state.toLowerCase();
						self.call_cloud_action('Cloud Folder Mapping',
						'cloud.folder.mapping',
						[['state','=',state]],
						[[false,'list'],[false,'form']])
					}
				},
			},
		});
	}

	render_file_doughnut_graph () {
		let self = this;
		$('#cloud_dashboard_file').replaceWith($('<canvas/>',{id:'cloud_dashboard_file'}))
		var chart = new Chart('cloud_dashboard_file',{
			type: 'doughnut',
			data: {
				labels: Object.keys(self.file_data),
				datasets: [{
					data: Object.values(self.file_data),
					backgroundColor:self.file_colors
				}],
			},
			options: {
				maintainAspectRatio: false,
				responsive: true,
				cutout: "70%",
				aspectRatio: 1.7,
				plugins: {
					legend: {
						display:true,
						position: 'bottom',
					},
					title: {
                        display: true,
                        text: self.total_file_sum,
                        padding: 2,
						position: 'top',
                    },
				},
				cutoutPercentage:80,
				// elements:{
				// 	center: {
				// 		text: self.total_file_sum,
				// 		color: '',
				// 		sidePadding: 10
				// 	}
				// },
				onClick (e,i){
					if (i.length) {
						var state = chart.data.labels[i[0].index]
						state =  state.toLowerCase();
						if (state=='update')
							state='need_sync'
						self.call_cloud_action(
							'Cloud File Mapping',
							'cloud.odoo.file.mapping',
							[['state','=',state]],
							[[false,'list'],[false,'form']]

						)
					}
				},
			},
		});
	}

}

CloudDashboard.template = "cloud_dashboard_template"
registry.category("actions").add('dashboard_cloud',CloudDashboard)
