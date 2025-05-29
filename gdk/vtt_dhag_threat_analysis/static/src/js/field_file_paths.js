odoo.define('vtt.field_file_paths', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var FieldChar = require('web.basic_fields').FieldChar;
var core = require('web.core');
var ajax = require('web.ajax');
var field_registry = require('web.field_registry');
var field_utils = require('web.field_utils');

var QWeb = core.qweb;
var _t = core._t;

var FieldFilePaths = AbstractField.extend({

    init: function(){
        this._super.apply(this, arguments);

        this.input_data = {
            insert_path_value: ''
        };
        this.json_data = {'paths': []};
        if(this.value == "")
            this.value = "{'paths': []}";
        if(this.value){
            try{
                this.json_data = jQuery.parseJSON(this.value);
            }catch(ex){
                this.json_data = {'paths': []};
            }
        }
    },

    /**
     * @private
     * @override
     */
    _render: function() {
        var self = this;

        this.$el.html('');
        this.$container = $(QWeb.render("FieldFilePaths", {widget: this}));

        if(this.mode != 'edit'){

        }
        else {
            this.$container.off('click', '.add-path').on('click', '.add-path', this._on_addPath_click.bind(this));
            this.$inputInsertPath = $(this.$container.find('input[name="txtAddPath"]'));
        }
        this.$container.appendTo(this.$el);
        this.$content_box = $(this.$container.find('.content-box'));
        this._renderDirectory();
    },

    _renderDirectory: function(){
        var self = this;

        //this.json_data.paths = ['abc', 'ccc'];
        this.$content_box.empty();

        if(this.mode != 'edit'){
            var $table = $(QWeb.render("FieldFilePaths.Table", {
                records: self.json_data.paths
            }));
            $table.appendTo(this.$content_box);
        }
        else {
            var $table = $(QWeb.render("FieldFilePaths.TableEdit", {
                records: self.json_data.paths
            }));
            $table.off('change', '.o_input').on('change', '.o_input', this._on_editPath_click.bind(this));
            $table.off('click', '.fp_delete_button').on('click', '.fp_delete_button', this._removePath.bind(this));
            $table.off('click', '.fp_edit_button').on('click', '.fp_edit_button', this._on_editPath_click.bind(this));
            $table.appendTo(this.$content_box);
        }
    },

    _on_editPath_click: function(ev){
        var self = this;
        var t = $(ev.currentTarget);

        var tr = $(t.closest('.data-row'));
        var input = $(tr.find('.o_input'));

//        if(tr.hasClass('edit-mode')){
            var rid = tr.attr('row_id');
            var value = input.val();

            self._updatePath(value, rid);
//            tr.removeClass('edit-mode');
//        }else{
//            this.$content_box.find('.data-row').removeClass('edit-mode');
//            tr.addClass('edit-mode');
//        }
        if(input.length > 0)
            input.focus();
    },

    _on_addPath_click: function(ev){
        var self = this;

        var value = this.$inputInsertPath.val();
        this._addPath(value);
    },

    _updatePath: function(value, row_id){
        var self = this;

        var row = this.json_data.paths.find(r => r.row_id == row_id);
        row.path = value;
        self._setValue(JSON.stringify(this.json_data));
        this._renderDirectory();
    },

    _addPath: function(value){
        var self = this;
        var row_id = Date.now();

        var data = { 'row_id': row_id, 'path': value };
        this.json_data.paths.push(data);
        this._renderDirectory();
        this.$inputInsertPath.val('');

        self._setValue(JSON.stringify(this.json_data));
    },

    _removePath: function(ev){
        var self = this;

        var t = $(ev.currentTarget);
        var id = t.data('row_id');

        if(id > 0){
            this.json_data.paths = _.reject(this.json_data.paths, function(item){ return item.row_id == id; });
            //this.value = JSON.stringify(this.json_data.paths);
            this._renderDirectory();

            this._setValue(JSON.stringify(this.json_data));
        }
    },
});

field_registry.add('field_file_paths', FieldFilePaths);

return {
    FieldFilePaths: FieldFilePaths
};

});
