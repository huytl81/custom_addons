odoo.define('vtt.investigate_select_create_dialogs', function(require){
    "use strict";

    var core = require('web.core');
//    var registry = require('web.widget_registry');
//    var registry = require('web.field_registry');

//    var session = require('web.session');
//    var rpc = require('web.rpc');

    var Widget = require('web.Widget');
    var relational_fields = require('web.relational_fields');
    var dialogs = require('web.view_dialogs');
//    var QWeb = core.qweb;

    var _t = core._t;

    var InvestigateSelectCreateDialog  = dialogs.SelectCreateDialog.extend({

        init: function(){
            this._super.apply(this, arguments);
            this.create_new_record = this.options.create_new_record || (function () {});
        },



        _prepareButtons: function () {
            var self = this;
            this.__buttons = [{
                text: _t("Cancel"),
                classes: 'btn-secondary o_form_button_cancel',
                close: true,
            }];
            if (!this.options.no_create) {
                this.__buttons.unshift({
                    text: _t("Create"),
                    classes: 'btn-primary',
                    click: this.create_new_record.bind(this),
                });
            }
            if (!this.options.disable_multiple_selection) {
                this.__buttons.unshift({
                    text: _t("Select"),
                    classes: 'btn-primary o_select_button',
                    disabled: true,
                    close: true,
                    click: function () {
                        var records = this.viewController.getSelectedRecords();
                        var values = _.map(records, function (record) {
                            return {
                                id: record.res_id,
                                display_name: record.data.display_name,
                            };
                        });
                        this.on_selected(values);
                    },
                });
            }
        },

    });

    return {InvestigateSelectCreateDialog:InvestigateSelectCreateDialog,};
});