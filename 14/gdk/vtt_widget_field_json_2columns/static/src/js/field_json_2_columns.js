odoo.define('vtt_widgets.field_json_2_columns', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var FieldChar = require('web.basic_fields').FieldChar;
var core = require('web.core');
var field_registry = require('web.field_registry');
var field_utils = require('web.field_utils');

var QWeb = core.qweb;
var _t = core._t;

var FieldJson2Columns = AbstractField.extend({
    _render: function() {
        var self = this;
        var info = JSON.parse(this.value);

        this.$el.html(QWeb.render('FieldJsonTable', {
            'records' : info
        }));
        this.$el.css("width", "100%");
        this.$el.attr('style', 'display: block !important');
    },

});

field_registry.add('field_json_2_columns', FieldJson2Columns);

return {
    FieldJson2Columns: FieldJson2Columns
};

});
