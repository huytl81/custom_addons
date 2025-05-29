odoo.define('vtt_widgets.json_table_2_columns', function(require){
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
        },
        events: {
//            'click .available_task': 'task_available',
        },
        init: function(){
            this._super.apply(this, arguments);

            this.context = arguments[1];
            this.attrs = arguments[2].attrs;

            this.options = JSON.parse(this.attrs.options.replace(/'/g, '"'));

            this.field_name = this.options.field_name;

            this.modelData = this.context.data;

        },

        willStart: function() {
            var self = this;
            return $.when(ajax.loadLibs(this), this._super()).then(function() {
                return self.fetchhData();
            });
        },

        start: function(){
            var super_render = this._super;
            var self = this;

            return this._super().then(function() {
                self.render();
            });
        },

        render: function() {
            var self = this;

            var info = JSON.parse(this.modelData[this.field_name]);

            this.$el.html(QWeb.render('FieldJsonTable', {
                'records' : info
            }));
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
        },

        //load data
        fetchhData: function(){
            var self = this;
        },
    });

    registry.add('json_table_2_columns', AttachmentBox);

    return {AttachmentBox:AttachmentBox,};
});