odoo.define('vtt.ProductProductMaterialListController', function (require) {
"use strict";

var core = require('web.core');
var ListController = require('web.ListController');

var _t = core._t

var qweb = core.qweb;


var ProductProductMaterialListController = ListController.extend({

    // -------------------------------------------------------------------------
    // Public
    // -------------------------------------------------------------------------

    init: function (parent, model, renderer, params) {
        this.context = renderer.state.getContext();
        return this._super.apply(this, arguments);
    },

    /**
     * @override
     */
    renderButtons: function ($node) {
        this._super.apply(this, arguments);
        if (this.context.no_at_date) {
            return;
        }
        var $buttonToDate = $(qweb.render('VttProductProductMaterial.Buttons'));
        $buttonToDate.on('click', this._onOpenWizard.bind(this));
        this.$buttons.prepend($buttonToDate);
    },
    _onOpenWizard: function () {
        var self = this;
        var state = this.model.get(this.handle, {raw: true});
        var stateContext = state.getContext();
        let activeIds = this.getSelectedIds();
        let materialId = stateContext.material_template_id;
        if (activeIds.length > 0) {
            this._rpc({
                model: 'vtt.product.material.template',
                method: 'update_material_products',
                args: [materialId, activeIds],
            }).then(function () {
                self.trigger_up('close_dialog');
//                this.do_action({
//                    type: 'ir.actions.act_window_close',
//                });
            });
        }
    },
});

return ProductProductMaterialListController;

});
