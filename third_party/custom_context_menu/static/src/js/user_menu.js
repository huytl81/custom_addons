/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import { registry } from "@web/core/registry";
import { ORM } from "@web/core/orm_service";
import { browser } from "@web/core/browser/browser";
let contextMenusEnabled = session?.contextmenu_enabled;

export function context_menu(env)  {
    return {
        type: "switch",
        id: "context_menu.menu",
        description: _t("Custom Menu"),
        callback: async () => {
            var orm = new ORM()
            contextMenusEnabled = await orm.call("res.users", "switch_contextmenu_enabled", [!contextMenusEnabled]);
            browser.location.reload();
        },
        isChecked: contextMenusEnabled,
        sequence: 30,
    }
}
registry.category("user_menuitems").add('context_menu.menu', context_menu)