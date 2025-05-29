odoo.define('vtt.InventoryReportListView', function (require) {
"use strict";

var ListView = require('web.ListView');
var InventoryReportListController = require('vtt.InventoryReportListController');
var viewRegistry = require('web.view_registry');


var InventoryReportListView = ListView.extend({
    config: _.extend({}, ListView.prototype.config, {
        Controller: InventoryReportListController,
    }),
});

viewRegistry.add('vtt_inventory_report_list', InventoryReportListView);

return InventoryReportListView;

});
