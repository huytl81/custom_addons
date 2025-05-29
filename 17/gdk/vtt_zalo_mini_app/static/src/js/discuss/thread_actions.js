/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { SearchProductsPanel } from "@vtt_zalo_mini_app/js/discuss/search_products_panel"; // Đảm bảo đường dẫn chính xác

const threadActionsRegistry = registry.category("mail.thread/actions");

threadActionsRegistry.add("search-products", {
    component: SearchProductsPanel,
    condition(component) {
        // Điều kiện để hiển thị panel tìm kiếm sản phẩm
        return component.thread && ["discuss.channel", "mail.box"].includes(component.thread.model);
    },
    panelOuterClass: "o-mail-SearchProductsPanel", // CSS class cho panel
    icon: "oi oi-fw oi-search", // Icon cho nút mở panel
    iconLarge: "oi oi-fw oi-search",
    name: _t("Search Products"),
    nameActive: _t("Close Product Search"),
    sequence: 18, // Đặt thứ tự hiển thị
    toggle: true, // Cho phép bật/tắt panel
});