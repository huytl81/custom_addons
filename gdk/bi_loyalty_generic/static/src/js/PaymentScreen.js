/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import {ErrorPopup} from "@point_of_sale/app/errors/popups/error_popup";
import { ConnectionLostError } from "@web/core/network/rpc_service";

patch(PaymentScreen.prototype, {

	async _finalizeValidation() {
		var self = this;
        if (this.currentOrder.is_paid_with_cash() || this.currentOrder.get_change()) {
            this.hardwareProxy.openCashbox();
        }

        this.currentOrder.date_order = luxon.DateTime.now();
        for (const line of this.paymentLines) {
            if (!line.amount === 0) {
                this.currentOrder.remove_paymentline(line);
            }
        }
        this.currentOrder.finalized = true;

        // 1. Save order to server.
        this.env.services.ui.block();
        const syncOrderResult = await this.pos.push_single_order(this.currentOrder);
        this.env.services.ui.unblock();

        if (syncOrderResult instanceof ConnectionLostError) {
            this.pos.showScreen(this.nextScreen);
            return;
        } else if (!syncOrderResult) {
            return;
        }

        try {
            // 2. Invoice.
            if (this.shouldDownloadInvoice() && this.currentOrder.is_to_invoice()) {
                if (syncOrderResult[0]?.account_move) {
                    await this.report.doAction("account.account_invoices", [
                        syncOrderResult[0].account_move,
                    ]);
                } else {
                    throw {
                        code: 401,
                        message: "Backend Invoice",
                        data: { order: this.currentOrder },
                    };
                }
            }
        } catch (error) {
            if (error instanceof ConnectionLostError) {
                Promise.reject(error);
                return error;
            } else {
                throw error;
            }
        }

        // 3. Post process.

        if (self.pos.get_order().get_partner()){
			let get_loyalty = this.pos.get_order().get_partner().id
			await this.orm.call(
				'res.partner',
				'updated_rec',
				[get_loyalty],
			).then(function(loyalty_point) {
				if (loyalty_point)
				{
					self.currentOrder.get_partner().loyalty_pts = loyalty_point;
				}
			});
		}


        if (
            syncOrderResult &&
            syncOrderResult.length > 0 &&
            this.currentOrder.wait_for_push_order()
        ) {
            await this.postPushOrderResolve(syncOrderResult.map((res) => res.id));
        }

        await this.afterOrderValidation(!!syncOrderResult && syncOrderResult.length > 0);
    }

    
});
