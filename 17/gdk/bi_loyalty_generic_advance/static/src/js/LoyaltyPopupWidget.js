/** @odoo-module */

import { LoyaltyPopupWidget } from "@bi_loyalty_generic/js/LoyaltyPopupWidget"; 
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
let redeem;

export class LoyaltyPopupWidgetAdvance extends LoyaltyPopupWidget {
    setup() {
        super.setup();
    }

    calculate_loyalty_points(){
                let self = this;
                let order = this.env.pos.get_order();
                let orderlines = order.get_orderlines();
                let partner = this.props.partner;
                let loyalty_settings = this.env.pos.pos_loyalty_setting;
                self.partner = partner || {};
                self.loyalty = partner.loyalty_pts;
                if(loyalty_settings.length != 0){
                    loyalty_settings.forEach(function(config){
                        if(config.active == true && config.loyalty_tier[0] == partner.tier_id[0]){
                            let product_id = config.product_id[0];
                            let product = self.env.pos.db.get_product_by_id(product_id);
                            self.product = product;
                            if(config.redeem_ids.length != 0){
                                let redeem;
                                let redeem_arr = []
                                for (let i = 0; i < config.redeem_ids.length; i++) {
                                    for (let j = 0; j < self.env.pos.pos_redeem_rule.length; j++) {
                                        if(config.redeem_ids[i] == self.env.pos.pos_redeem_rule[j].id)
                                        {
                                            redeem_arr.push(self.env.pos.pos_redeem_rule[j]);
                                        }
                                    }
                                }
                                for (let j = 0; j < redeem_arr.length; j++) {
                                    if( redeem_arr[j].min_amt <= partner.loyalty_pts && partner.loyalty_pts <= redeem_arr[j].max_amt)
                                    {
                                        redeem = redeem_arr[j];
                                        break;
                                    }
                                }
                                if(redeem){
                                    let point_value = redeem.reward_amt * self.loyalty;
                                    if (partner){
                                        self.loyalty_amount = point_value;
                                        partner.loyalty_amount = point_value;
                                    }
                                }
                            }
                        }
                    });
                    
                }
            }

            redeemPoints() {
                let self = this;
                let order = this.env.pos.get_order();
                let orderlines = order.get_orderlines();
                let entered_code = $("#entered_item_qty").val();
                let point_value = 0;
                let remove_line;    
                let partner = this.props.partner;
                let loyalty = partner.loyalty_pts;
                let loyalty_settings = this.env.pos.pos_loyalty_setting;
                if(entered_code<0)
                {
                    alert('Please enter valid amount.');
                    return
                }
                if(loyalty_settings.length != 0){
                    loyalty_settings.forEach(function(config){
                        if(config.active == true && config.loyalty_tier[0] == partner.tier_id[0]){
                            if(config.redeem_ids.length != 0){
                                let redeem;
                                let redeem_arr = []
                                for (let i = 0; i < config.redeem_ids.length; i++) {
                                    for (let j = 0; j < self.env.pos.pos_redeem_rule.length; j++) {
                                        if(config.redeem_ids[i] == self.env.pos.pos_redeem_rule[j].id)
                                        {
                                            redeem_arr.push(self.env.pos.pos_redeem_rule[j]);
                                        }
                                    }
                                }
                                for (let j = 0; j < redeem_arr.length; j++) {
                                    if( redeem_arr[j].min_amt <= partner.loyalty_pts && partner.loyalty_pts <= redeem_arr[j].max_amt)
                                    {
                                        redeem = redeem_arr[j];
                                        break;
                                    }
                                }
                                if(redeem && redeem.min_amt <= loyalty &&  loyalty<= redeem.max_amt)
                                {
                                    if(entered_code <= loyalty)
                                    {
                                        let total = order.get_total_with_tax();
                                        let redeem_value = redeem.reward_amt * entered_code
                                        if (redeem_value > total) {
                                            alert('Please enter valid amountss.')
                                        }
                                        if (redeem_value <= total) {
                                            order.add_product(self.product, {
                                                price: -redeem_value
                                            });
                    
                                            partner.loyalty_pts -= entered_code;
                                            remove_line = orderlines[orderlines.length-1].id
                                            order.redeemed_points = entered_code;
                                            order.redeem_done = true;
                                            order.redeem_point = entered_code;
                                            order.remove_line = remove_line;
                                            self.cancel();
                                        }
                                    }
                                    else{
                                        alert('Please enter valid amount.');
                                    }
                                }
                                else{
                                    alert("limit exceeded");
                                }
                            }
                           
                        }
                    });
                    
                }   
                          
            }

}
