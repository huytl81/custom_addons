odoo.define('vtt_widgets.json_table_dynamic_columns', function(require){
    "use strict";

    var core = require('web.core');
    var registry = require('web.widget_registry');

    var session = require('web.session');
    var rpc = require('web.rpc');
    var ajax = require('web.ajax');

    var Widget = require('web.Widget');
    var QWeb = core.qweb;

    var _t = core._t;

    var AttachmentBox = Widget.extend({
//        template: "gk.AttachmentBox",
        cssLibs: [
//            '/web/static/lib/nvd3/nv.d3.css'
        ],
        jsLibs: [
        ],
        custom_events: {
//            v_reload_attachment_box: '_onReloadAttachmentBox',
//            v_delete_attachment: '_onDeleteAttachment',
//            v_checked_permission: '_onCheckedPermission'
        },
        events: {
//            'click .available_task': 'task_available',
        },
        init: function(){
            this._super.apply(this, arguments);

//            console.log('init');
//            console.log(this);
//            console.log(arguments);

            this.context = arguments[1];
            this.attrs = arguments[2].attrs;

//            console.log(this.attrs.options.replace('\'', '\"'));

            this.options = JSON.parse(this.attrs.options.replace(/'/g, '"'));

            this.field_name = this.options.field_name;
            this.fields = this.options.fields;
            this.headers = this.fields;
            if(this.options.headers)
                this.headers = this.options.headers;

            this.modelData = this.context.data;

//            console.log(this);

//            this.attachments = [];
//            this.context = arguments[1];
//            this.model = this.context.model;
//            this.res_id = this.context.res_id;
        },

        willStart: function() {
            var self = this;

//            console.log('will start');

            //trong ajax co function loadLibs se truy cap vao field jsLibs cua doi tuong truyen vao (tham so)
            return $.when(ajax.loadLibs(this), this._super()).then(function() {
                return self.fetchhData();
            });
        },

        start: function(){
            var super_render = this._super;
            var self = this;

//            console.log('start');

            return this._super().then(function() {
                self.render();
            });
        },

        render: function() {
            var self = this;

//            var info = [
//                {'title': 'cccc', 'content': 'connnnnnnnn'}
//            ];

            var info = JSON.parse(this.modelData[this.field_name]);
            var fields = ['title', 'content'];
            var headers = ['Title toe', 'Con teng'];

            if(this.fields)
                fields = this.fields;
            if(this.headers)
                headers = this.headers;

            var table_class = 'o_list_table table table-sm table-hover table-striped';
            var wrapper = $('<div></div>');
            var table = $('<table><tbody></tbody></table>');
            table.addClass(table_class);

            //add header row
            var $rowHeader = $('<tr></tr>');
            headers.forEach(function(name, index, arr){ $rowHeader.append('<td><strong>' + name + '</strong></td>') });
            $rowHeader.appendTo(table);

            //add data rows
            info.forEach(function(record, index, arr){
                var row = self._getRow(fields, record);
                row.appendTo(table);
            });

            table.appendTo(wrapper);

            this.$el.html('');
            wrapper.appendTo(this.$el);
        },

        _getRow: function(fields, record){
            var $row = $('<tr></tr>');
            fields.forEach(function(name, index, arr){
                var value = record[name] == undefined ? '' : record[name];
                $row.append('<td>' + value + '</td>')
            });
            return $row;
        },

        renderAttachmentBox: function(){
            var self = this;
            self.$attachmentBox = self.$el.find('.vtt_attachment_box');

            var re = new MailAttachmentBox(self, self.context, self.attachments);

            self.$attachmentBox.empty();
            re.appendTo(self.$attachmentBox);
        },

        reload: function(){
            var self = this;

//            if(self.$attachmentBox){
//                self.$attachmentBox.empty();
//            }
//
//            var def1 = self.fetchhData();
//
//            $.when(def1).done(function(){
//                self.render();
//            });
        },

        //load data
        fetchhData: function(){
            var self = this;

//            var def1 =  this._rpc({
//                model: 'ir.attachment',
//                method: 'search_read',
//                kwargs: {
//                    domain: [
//                        '&', ['c_model', '=', this.model], ['c_id', '=', this.res_id]
//                    ],
//                    fields: ['filename', 'name', 'datas_fname', 'id', 'mimetype', 'type', 'url'],
//                    //limit: 5,
//                    order: [{name: 'id', asc: false}],
//                },
//            }).done(function(result) {
//                if(result){
//                    self.attachments = result;
//                }
//            });
//
//            return $.when(def1).done(function(){
//            });
        },
    });

    registry.add('json_table_dynamic_columns', AttachmentBox);

    return {AttachmentBox:AttachmentBox,};
});