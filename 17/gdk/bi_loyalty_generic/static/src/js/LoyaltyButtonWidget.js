/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import {ErrorPopup} from "@point_of_sale/app/errors/popups/error_popup";
import { LoyaltyPopupWidget } from "@bi_loyalty_generic/js/LoyaltyPopupWidget"; 
export class LoyaltyButton extends Component {
    static template = "bi_loyalty_generic.LoyaltyButton";

    setup() {
        this.pos = usePos();
    }

    async onClick() {
        let order = this.pos.get_order();
        let self = this;
        let partner = false;
        let loyalty_points = 0;
        if (order.orderlines.length > 0) {
            if (this.pos.pos_loyalty_setting.length != 0) {
                if (order.get_partner() != null) {
                    partner = order.get_partner();
                    loyalty_points = partner.loyalty_pts;
                }
                if (order.redeem_done) {
                    this.pos.popup.add(ErrorPopup, {
                        title: _t('Redeem Product'),
                        body: _t('Sorry, you already added the redeem product.'),
                    });
                } else if (this.pos.pos_loyalty_setting[0].redeem_ids.length == 0) {
                    this.pos.popup.add(ErrorPopup, {
                        title: _t('No Redemption Rule'),
                        body: _t('Please add Redemption Rule in loyalty configuration'),
                    });
                } else if (!partner) {
                    this.pos.popup.add(ErrorPopup, {
                        title: _t('Unknown customer'),
                        body: _t('You cannot redeem loyalty points. Select customer first.'),
                    });
                } else if (loyalty_points < 1) {
                    this.pos.popup.add(ErrorPopup, {
                        title: _t('Insufficient Points'),
                        body: _t('Sorry, you do not have sufficient loyalty points.'),
                    });
                } else {
                    this.pos.popup.add(LoyaltyPopupWidget, {'partner': partner});
                }
            }
        } else {
            this.pos.popup.add(ErrorPopup, {
                title: _t('Empty Order'),
                body: _t('Please select some products'),
            });
        }
    }

    
}

ProductScreen.addControlButton({
    component: LoyaltyButton,
    position: ["before", "SetFiscalPositionButton"],
    condition: function () {
        if (this.pos.pos_loyalty_setting.length > 0) {
            return true;
        } else {
            return false;
        }
    },
});
