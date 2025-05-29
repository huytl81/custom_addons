odoo.define('vtt.ProductProductMaterialListView', function (require) {
"use strict";

var ListView = require('web.ListView');
var ProductProductMaterialListController = require('vtt.ProductProductMaterialListController');
var viewRegistry = require('web.view_registry');


var ProductProductMaterialListView = ListView.extend({
    config: _.extend({}, ListView.prototype.config, {
        Controller: ProductProductMaterialListController,
    }),
});

viewRegistry.add('vtt_product_product_material_list', ProductProductMaterialListView);

return ProductProductMaterialListView;

});
