/* @odoo-module */

// import { Component, onWillUpdateProps, useExternalListener, useState } from "@odoo/owl";
// import { useAutofocus } from "@web/core/utils/hooks";
// import { useMessageSearch } from "@mail/core/common/message_search_hook";
// import { browser } from "@web/core/browser/browser";
// import { ActionPanel } from "@mail/discuss/core/common/action_panel";
// // import { MessageCardList } from "./message_card_list";
// import { _t } from "@web/core/l10n/translation";

// /**
//  * @typedef {Object} Props
//  * @property {import("@mail/core/common/thread_model").Thread} thread
//  * @property {string} [className]
//  * @property {funtion} [closeSearch]
//  * @property {funtion} [onClickJump]
//  * @extends {Component<Props, Env>}
//  */
// export class SearchProductsPanel extends Component {
//     static components = {
//         // MessageCardList,
//         ActionPanel,
//     };
//     static props = ["thread", "className?", "closeSearch?", "onClickJump?"];
//     static template = "vtt_zalo_mini_app.SearchProductsPanel";

//     setup() {
//         this.state = useState({ searchTerm: "", searchedTerm: "" });
//         this.messageSearch = useMessageSearch(this.props.thread);
//         useAutofocus();
//         useExternalListener(
//             browser,
//             "keydown",
//             (ev) => {
//                 if (ev.key === "Escape") {
//                     this.props.closeSearch?.();
//                 }
//             },
//             { capture: true }
//         );
//         onWillUpdateProps((nextProps) => {
//             if (this.props.thread.notEq(nextProps.thread)) {
//                 this.env.searchMenu?.close();
//             }
//         });
//     }

//     get title() {
//         return _t("Search messages");
//     }

//     get MESSAGES_FOUND() {
//         if (this.messageSearch.messages.length === 0) {
//             return false;
//         }
//         return _t("%s messages found", this.messageSearch.count);
//     }

//     search() {
//         this.messageSearch.searchTerm = this.state.searchTerm;
//         this.messageSearch.search();
//         this.state.searchedTerm = this.state.searchTerm;
//     }

//     clear() {
//         this.state.searchTerm = "";
//         this.state.searchedTerm = this.state.searchTerm;
//         this.messageSearch.clear();
//         this.props.closeSearch?.();
//     }

//     /** @param {KeyboardEvent} ev */
//     onKeydownSearch(ev) {
//         if (ev.key !== "Enter") {
//             return;
//         }
//         if (!this.state.searchTerm) {
//             this.clear();
//         } else {
//             this.search();
//         }
//     }

//     onLoadMoreVisible() {
//         const before = this.messageSearch.messages
//             ? Math.min(...this.messageSearch.messages.map((message) => message.id))
//             : false;
//         this.messageSearch.search(before);
//     }
// }



// /** @odoo-module **/

import { Component, onWillUpdateProps, useExternalListener, useState } from "@odoo/owl";
import { useAutofocus, useService } from "@web/core/utils/hooks";
import { browser } from "@web/core/browser/browser";
import { ActionPanel } from "@mail/discuss/core/common/action_panel";
import { _t } from "@web/core/l10n/translation";

export class SearchProductsPanel extends Component {
    static components = {
        ActionPanel,
    };
    static props = ["closeSearch?", "onClickJump?", 'thread'];
    static template = "vtt_zalo_mini_app.SearchProductsPanel";

    setup() {
        this.rpc = useService("rpc");
        this.orm = useService("orm");
        this.state = useState({ searchTerm: "", searchedTerm: "", products: [], searching: false });
        useAutofocus();
        useExternalListener(
            browser,
            "keydown",
            (ev) => {
                if (ev.key === "Escape") {
                    this.props.closeSearch?.();
                }
            },
            { capture: true }
        );
    }

    get title() {
        return _t("Search products");
    }

    async onClickJump(productName, productId) {
        console.log(this.props.thread);

        // Lấy thông tin discuss channel hiện tại
        const thread = this.props.thread;

        // Lấy thông tin user hiện tại
        const currentUser = this.env.user;

        const currentHost = window.location.host;

        console.log(currentUser);

        // Gửi tin nhắn "Xin chao" đến discuss channel hiện tại
        await this.rpc('/web/dataset/call_kw', {
            model: 'discuss.channel',
            method: 'message_post',
            args: [thread.id],
            kwargs: {
                product_id: productId,
                product_name: productName,
                body: '[Đã gửi ảnh SP: ' + productName + ']',
                message_type: 'comment',
                subtype_xmlid: 'mail.mt_comment',
                author_id: -1,
                product_url: currentHost + '/image/product/' + productId,
            },
        });

        // Thực hiện các hành động khác nếu cần
        // await new Promise((resolve) => setTimeout(() => requestAnimationFrame(resolve)));
        // await this.env.messageHighlight?.highlightMessage(message, this.props.thread);
    }

    search() {
        this.state.searching = true;
        console.log(this.state.searchTerm);
        this.orm.call("product.template", "search_read", [], {
            fields: ["id", "name", "list_price", "image_128"],
            domain: [["name", "ilike", this.state.searchTerm]],
        }).then((products) => {
            this.state.products = products;
            this.state.searchedTerm = this.state.searchTerm;
            this.state.searching = false;
        });

        // this.rpc('/web/dataset/call_kw/', {
        //     model: "product.template",
        //     method: "search_read",
        //     domain: [["name", "ilike", this.state.searchTerm]],
        //     args:[[]],
        //     kwargs: { fields: ["id", "name"] },
        // }).then((products) => {
        //     this.state.products = products;
        //     this.state.searchedTerm = this.state.searchTerm;
        //     this.state.searching = false;
        // });
    }

    clear() {
        this.state.searchTerm = "";
        this.state.searchedTerm = this.state.searchTerm;
        this.state.products = [];
        this.state.searching = false;
        this.props.closeSearch?.();
    }

    onKeydownSearch(ev) {
        if (ev.key !== "Enter") {
            return;
        }
        if (!this.state.searchTerm) {
            this.clear();
        } else {
            this.search();
        }
    }
}