odoo.define('vtt.CampaignListView', function (require) {
"use strict";

var ListView = require('web.ListView');
var CampaignListController = require('vtt.CampaignListController');
var viewRegistry = require('web.view_registry');


var CampaignListView = ListView.extend({
    config: _.extend({}, ListView.prototype.config, {
        Controller: CampaignListController,
    }),
});

viewRegistry.add('vtt_campaign_import_list', CampaignListView);

return CampaignListView;

});
