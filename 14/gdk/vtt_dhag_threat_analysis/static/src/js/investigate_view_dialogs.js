odoo.define('vtt.many2many_malware_investigate', function(require){
    "use strict";

    var core = require('web.core');
//    var registry = require('web.widget_registry');
    var registry = require('web.field_registry');

    var session = require('web.session');
    var rpc = require('web.rpc');

    var Widget = require('web.Widget');
    var relational_fields = require('web.relational_fields');
    var dialogs = require('web.view_dialogs');
    var vtt_dialogs = require('vtt.investigate_select_create_dialogs');
//    var QWeb = core.qweb;

    var _t = core._t;

    var Many2manyInvestigateMalware  = relational_fields.FieldMany2Many.extend({

        onAddRecordOpenDialog: function () {
            var self = this;
            var domain = this.record.getDomain({fieldName: this.name});

            new vtt_dialogs.InvestigateSelectCreateDialog(this, {
                res_model: this.field.relation,
                domain: domain.concat(["!", ["id", "in", this.value.res_ids]]),
                context: this.record.getContext(this.recordParams),
                title: _t("Add: ") + this.string,
                no_create: this.nodeOptions.no_create || !this.activeActions.create || !this.canCreate,
                fields_view: this.attrs.views.form,
                kanban_view_ref: this.attrs.kanban_view_ref,
                create_new_record: function () {
                    console.log('Start over here');
                    var dialog = new dialogs.FormViewDialog(this, _.extend({}, this.options, {
                        on_saved: function (record) {
                            var values = [{
                                id: record.res_id,
                                display_name: record.data.display_name || record.data.name,
                            }];
                            self._setValue({
                                operation: 'ADD_M2M',
                                ids: values,
                            });
                            console.log(values);
                        },
                    })).open();
                    dialog.on('closed', this, this.close);
//                    return dialog;
                },
                on_selected: function (records) {
                    var resIDs = _.pluck(records, 'id');
                    var newIDs = _.difference(resIDs, self.value.res_ids);
                    if (newIDs.length) {
                        var news = rpc.query({
                            model: 'threat.malware',
                            method: 'new_copy_from_ids',
                            args: [newIDs]
                        }).then(function(news_ids){
                            var values = _.map(news_ids, function (id) {
                                return {id: id};
                            });
                            self._setValue({
                                operation: 'ADD_M2M',
                                ids: values,
                            });
                        }) ;
                    }
                }

            }).open();
        },

    });

    registry.add('many2many_malware_investigate', Many2manyInvestigateMalware);

    return {Many2manyInvestigateMalware:Many2manyInvestigateMalware,};
});