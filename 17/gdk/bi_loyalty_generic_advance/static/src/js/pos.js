/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    // @Override
    async _processData(loadedData) {
        await super._processData(...arguments);
        let self = this;
		self.pos_loyalty_tiers = loadedData['loyalty.tier.config'];
    },
});

patch(Order.prototype, {
    setup() {
        super.setup(...arguments);    
    },
    get_total_loyalty(){
		let final_loyalty = 0
		let order = this.pos.get_order();
		let orderlines = this.get_orderlines();
		let partner_id = this.get_partner();
		var self=this;
		if(order){
			if(partner_id){
				if(partner_id.tier_id){
					if(this.pos.pos_loyalty_setting.length != 0){						
						let pos_loyalty_setting = this.pos.pos_loyalty_setting;
						pos_loyalty_setting.forEach(function(config){
							let pos_loyalty_tiers= self.pos.pos_loyalty_tiers;
							pos_loyalty_tiers.forEach(function(tier){
								if(partner_id.total_sales >= tier.min_range && partner_id.total_sales <= tier.max_range){
									if(config.active == true && config.loyalty_tier[0] == partner_id.tier_id[0]){
										if (config.loyalty_basis_on == 'loyalty_category') {
											if (partner_id){
												let loyalty = 0;
												for (let i = 0; i < orderlines.length; i++) {
													let lines = orderlines[i];
													let cat_ids = self.pos.db.get_category_by_id(lines.product.bi_pos_reports_catrgory[0])
													if(cat_ids){
														if (cat_ids['Minimum_amount']>0){
															final_loyalty += lines.get_price_with_tax() / cat_ids['Minimum_amount'];
														}
													}
												}
												return parseFloat(final_loyalty.toFixed(2));
											}
										}
										else if (config.loyalty_basis_on == 'amount') {
											let loyalty_total = 0;
											if (order && partner_id){
												let amount_total = order.get_total_with_tax();
												let subtotal = order.get_total_without_tax();
												let loyaly_points = config.loyality_amount;
												final_loyalty += (amount_total / loyaly_points);
												if(order.get_partner()){
													loyalty_total = order.get_partner().loyalty_points1 + final_loyalty;							
												}
												return parseFloat(final_loyalty.toFixed(2));
											}
										}
									}
								}
							});
						});			
					}
					return parseFloat(final_loyalty.toFixed(2));
				}
				else{
					var self=this;
					if(self.pos.pos_loyalty_setting.length != 0){
						let pos_loyalty_setting = self.pos.pos_loyalty_setting;
						pos_loyalty_setting.forEach(function(config){
							let pos_loyalty_tiers= self.pos.pos_loyalty_tiers;
							pos_loyalty_tiers.forEach(function(tier){
								if(partner_id.total_sales >= tier.min_range && partner_id.total_sales <= tier.max_range){
									if(config.active == true && config.loyalty_tier[0] == tier.id){
										if (config.loyalty_basis_on == 'loyalty_category') {
											if (partner_id){
												let loyalty = 0;
												for (let i = 0; i < orderlines.length; i++) {
													let lines = orderlines[i];
													let cat_ids = self.pos.db.get_category_by_id(lines.product.bi_pos_reports_catrgory[0])
													if(cat_ids){
														if (cat_ids['Minimum_amount']>0){
															final_loyalty += lines.get_price_with_tax() / cat_ids['Minimum_amount'];
														}
													}
												}
												return parseFloat(final_loyalty.toFixed(2));
											}
										}
										else if (config.loyalty_basis_on == 'amount') {
											let loyalty_total = 0;
											if (order && partner_id){
												let amount_total = order.get_total_with_tax();
												let subtotal = order.get_total_without_tax();
												let loyaly_points = config.loyality_amount;
												final_loyalty += (amount_total / loyaly_points);
												if(order.get_partner()){
													loyalty_total = order.get_partner().loyalty_points1 + final_loyalty;							
												}
												return parseFloat(final_loyalty.toFixed(2));
											}
										}
									}
								}

							});

						});

					}
					return parseFloat(final_loyalty.toFixed(2));						
				}
				
			}
			
		}
		
	}
});

