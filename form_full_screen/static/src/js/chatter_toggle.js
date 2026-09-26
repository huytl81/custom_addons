/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { append, createElement, combineAttributes } from "@web/core/utils/xml";
import { FormCompiler } from "@web/views/form/form_compiler";
import { FormRenderer } from "@web/views/form/form_renderer";

// 1. Quản lý reactive state trực tiếp trên FormRenderer
patch(FormRenderer.prototype, {
    setup() {
        super.setup();
        this.state.isChatterCollapsed = false;
        this.toggleChatter = this.toggleChatter.bind(this);
    },
    toggleChatter() {
        const target = this?.state ? this : this?.__comp__;
        if (target && target.state) {
            target.state.isChatterCollapsed = !target.state.isChatterCollapsed;
        }
    },
});

// 2. Patch FormCompiler để bind reactive template
patch(FormCompiler.prototype, {
    compile(node, params) {
        const res = super.compile(node, params);
        const chatterNodes = res.querySelectorAll(".o-mail-Form-chatter");
        if (!chatterNodes.length) {
            return res; // Không có chatter, giữ nguyên
        }

        const formSheetBgXml = res.querySelector(".o_form_sheet_bg");
        if (!formSheetBgXml) {
            return res; // An toàn: không có sheet background thì không xử lý
        }

        // Ẩn chatter qua reactive class
        for (const chatterEl of chatterNodes) {
            combineAttributes(
                chatterEl,
                "t-attf-class",
                "{{ __comp__.state.isChatterCollapsed ? 'd-none' : '' }}"
            );
        }

        // Mở rộng form full-width qua reactive class
        combineAttributes(
            formSheetBgXml,
            "t-attf-class",
            "{{ __comp__.state.isChatterCollapsed ? 'max-width-unset' : '' }}"
        );

        // Tìm hoặc tạo statusbar để đặt nút toggle
        let statusbar = formSheetBgXml.querySelector(".o_form_statusbar");
        if (!statusbar) {
            statusbar = createElement("div", {
                class: "o_form_statusbar position-relative d-flex justify-content-between mb-0 mb-md-2 pb-2 pb-md-0",
            });
            const placeholder = createElement("div", { class: "me-auto" });
            append(statusbar, placeholder);
            formSheetBgXml.prepend(statusbar);
        }

        const webClientViewAttachmentViewHookXml = res.querySelector(".o_attachment_preview");
        const hasPreview = !!webClientViewAttachmentViewHookXml;

        // Tạo nút toggle chuẩn Owl với t-on-click dạng arrow function
        const hideChatterBtn = createElement("button", {
            type: "button",
            "t-attf-class": `{{ ["SIDE_CHATTER", "EXTERNAL_COMBO_XXL"].includes(__comp__.mailLayout(${hasPreview})) ? "btn btn-secondary o_chatter_toggle_btn ms-1" : "d-none" }} {{ __comp__.state.isChatterCollapsed ? 'collapsed' : '' }}`,
            "t-att-data-collapsed": "__comp__.state.isChatterCollapsed",
            "t-on-click": "() => __comp__.toggleChatter()",
            title: "Toggle Chatter / Full Screen",
        });

        const icon = createElement("i", {
            class: "oi oi-fw o_chatter_toggle_icon",
            "data-icon": "arrow_forward",
            role: "img",
            "aria-label": "Toggle Chatter",
        });
        append(hideChatterBtn, icon);
        append(statusbar, hideChatterBtn);

        return res;
    },
});