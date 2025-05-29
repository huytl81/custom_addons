odoo.define('vtt.field_instant_change_widget', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var basic_fields = require('web.basic_fields');
var fieldRegistry = require('web.field_registry');

var FieldChar = basic_fields.FieldChar;

var FieldCharInstantChange = FieldChar.extend({
    events: _.extend({}, FieldChar.prototype.events, {
        'input': '_onChangeInput',
    }),

    init: function (parent) {
            this._super.apply(this, arguments);
            this.parent = parent;
        },

    _onChangeInput: function (e) {
        var self = this;
        this._onChange();
//        self.$input.trigger('change');

    }
});

fieldRegistry.add('field_instant_change_widget', FieldCharInstantChange);

return {
    FieldCharInstantChange: FieldCharInstantChange,
};
});