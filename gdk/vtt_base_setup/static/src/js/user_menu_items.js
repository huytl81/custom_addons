/** @odoo-module **/

import { UserMenu } from "@web/webclient/user_menu/user_menu";
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
import { _t } from "@web/core/l10n/translation";
const userMenuRegistry = registry.category("user_menuitems");

//patch(UserMenu.prototype, {
//    setup() {
//        this._super.apply(this, arguments);
//        userMenuRegistry.remove("documentation");
//        userMenuRegistry.remove("support");
//        userMenuRegistry.remove("odoo_account");
//    },
//
//});

function documentationItemNew(env) {
    const documentationURL = "/web/client/user-documentation";
    return {
        type: "item",
        id: "vtt_documentation",
        description: _t("Documentation"),
        href: documentationURL,
        callback: () => {
            browser.open(documentationURL, "_blank");
        },
//        callback: async function () {
//            const actionDescription = await env.services.orm.call("res.users", "action_open_user_document");
//            actionDescription.res_id = env.services.user.userId;
//            env.services.action.doAction(actionDescription);
//        },
        sequence: 10,
    };
}

registry.category("user_menuitems").add("vtt_documentation", documentationItemNew);
registry.category("user_menuitems").remove("support");
registry.category("user_menuitems").remove("documentation");
registry.category("user_menuitems").remove("odoo_account");