/** @odoo-module */

import { session } from "@web/session";
import resConfigEdition from "@web/js/resConfigEdition";

//import { resConfigEdition } from "@web/core/registry";
//var Hamster = require('web.res_config_edition');

resConfigEdition.include({
    setup() {
        this.serverVersion = session.server_version;
        this.expirationDate = session.expiration_date
            ? DateTime.fromSQL(session.expiration_date).toLocaleString(DateTime.DATE_FULL)
            : DateTime.now().plus({ days: 365 }).toLocaleString(DateTime.DATE_FULL);
    }
});