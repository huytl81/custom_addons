/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { utils  } from "@web/core/ui/ui_service";
import {ErrorPopup} from "@point_of_sale/app/errors/popups/error_popup";
import { _t } from "@web/core/l10n/translation";

patch(PosStore.prototype, {
    // @Override
    async _processData(loadedData) {
        await super._processData(...arguments);
       	let self = this;
		self.pos_loyalty_setting = loadedData['all.loyalty.setting'];
		self.pos_redeem_rule = loadedData['all.redeem.rule'];
    },
    async _pushOrdersToServer() {
        const ordersUidsToSync = [...this.ordersToUpdateSet].map(order => order.uid);
        const ordersToSync = this.db.get_unpaid_orders_to_sync(ordersUidsToSync);
        const ordersResponse = await this._save_to_server(ordersToSync, {'draft': true});
        const tableOrders = [...this.ordersToUpdateSet].map(order => order);
        if(ordersResponse != true){
            ordersResponse.forEach(orderResponseData => this._updateTableOrder(orderResponseData, tableOrders));
        }
    },
    async selectPartner() {
        // FIXME, find order to refund when we are in the ticketscreen.
        const currentOrder = this.get_order();
        if(currentOrder.redeem_done){
			this.env.services.popup.add(ErrorPopup,{
				title: _t('Cannot Change Customer'),
				body: _t('Sorry, you redeemed product, please remove it before changing customer.'),
			}); 
		}else{
			super.selectPartner();
		}
    }
   
});

patch(Order.prototype, {
    setup() {
        super.setup(...arguments);
        this.loyalty = this.loyalty  || 0;
		this.redeemed_points = this.redeemed_points || 0;
		this.redeem_done = this.redeem_done || false;
		this.remove_true = this.remove_true || false;
		this.redeem_point = this.redeem_point || 0;
		this.remove_line = this.remove_line || false;
    },
    init_from_JSON(json){
		super.init_from_JSON(...arguments);			
		this.loyalty = json.loyalty;
		this.redeem_done = json.redeem_done;
		this.redeemed_points = json.redeemed_points;
		this.remove_true = json.remove_true || false;
		this.redeem_point = json.redeem_point || 0;
		this.remove_line = json.remove_line || false;
	},

	export_as_JSON(){
		const json = super.export_as_JSON(...arguments);			
		json.redeemed_points = this.redeemed_points;
		json.loyalty = this.get_total_loyalty();
		json.redeem_done = this.redeem_done;
		json.remove_true = this.remove_true || false;
		json.redeem_point = this.redeem_point || 0;
		json.remove_line = this.remove_line || false;
		return json;
	},

	removeOrderline(line) {
        this.redeem_done = false;
        if(line.id ==this.remove_line){
			this.remove_true = true;
			let partner = this.get_partner();
			if (partner) {
				partner.loyalty_points1 = partner.loyalty_points1 + parseFloat(this.redeem_point) ;
			}
		}
		else{
			this.remove_true = false;
		}
        super.removeOrderline(line);
    },
	get_redeemed_points(){
		return this.redeemed_points;
	},

	get_total_loyalty(){
		let round_pr = utils.round_precision;
		let round_di = utils.round_decimals;
		let rounding = this.pos.currency.rounding;
		let final_loyalty = 0
		let order = this.pos.get_order();
		let orderlines = this.get_orderlines();
		let partner_id = this.get_partner();
		if(this.pos.pos_loyalty_setting.length != 0)
		{				
		   if (this.pos.pos_loyalty_setting[0].loyalty_basis_on == 'loyalty_category') {
				if (partner_id){
					let loyalty = 0;
					for (let i = 0; i < orderlines.length; i++) {
						let lines = orderlines[i];
						let cat_ids = this.pos.db.get_category_by_id(lines.product.bi_pos_reports_catrgory[0])
						if(cat_ids){
							if (cat_ids['Minimum_amount']>0){
								final_loyalty += lines.get_price_with_tax() / cat_ids['Minimum_amount'];
							}
						}
					}
					return parseFloat(final_loyalty.toFixed(2));
				}
		   }else if (this.pos.pos_loyalty_setting[0].loyalty_basis_on == 'amount') {
				let loyalty_total = 0;
				if (order && partner_id){
					let amount_total = order.get_total_with_tax();
					let subtotal = order.get_total_without_tax();
					let loyaly_points = this.pos.pos_loyalty_setting[0].loyality_amount;
					final_loyalty += (amount_total / loyaly_points);
					if(order.get_partner()){
						loyalty_total = order.get_partner().loyalty_points1 + final_loyalty;							
					}
					return parseFloat(final_loyalty.toFixed(2));
				}
			}
		}
		return parseFloat(final_loyalty.toFixed(2));
	},

	export_for_printing() {
        const result = super.export_for_printing(...arguments);
        if (this.get_partner()) {
            result.partner = this.get_partner();
        }
        result.total_loyalty = this.get_total_loyalty();
        return result;
    },
});
