/** @odoo-module **/
import { session } from "@web/session";

import { SubscriptionManager } from "@web_enterprise/webclient/home_menu/enterprise_subscription_service";
//import { SubscriptionManager, enterpriseSubscriptionService } from "@web_enterprise/webclient/home_menu/enterprise_subscription_service";

SubscriptionManager.include({
    constructor(env, { rpc, orm, notification }) {
        this.env = env;
        this.rpc = rpc;
        this.orm = orm;
        this.notification = notification;
        if (session.expiration_date) {
            this.expirationDate = deserializeDateTime(session.expiration_date);
        } else {
            // If no date found, assume 1 year and hope for the best
            this.expirationDate = DateTime.utc().plus({ days: 365 });
        }
        this.expirationReason = session.expiration_reason;
        // Hack: we need to know if there is at least one app installed (except from App and
        // Settings). We use mail to do that, as it is a dependency of almost every addon. To
        // determine whether mail is installed or not, we check for the presence of the key
        // "notification_type" in session_info, as it is added in mail for internal users.
        this.hasInstalledApps = "notification_type" in session;
        // "user" or "admin"
        this.warningType = session.warning;
        this.lastRequestStatus = null;
        this.isWarningHidden = cookie.get("oe_instance_hide_panel");
    }
})