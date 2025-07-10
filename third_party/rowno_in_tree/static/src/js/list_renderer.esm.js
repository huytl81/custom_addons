/* @odoo-module */

import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";

patch(ListRenderer.prototype, {
    setup() {
        super.setup();
        onMounted(() => {
            var table = this.tableRef.el;
            if (table) {
                var childTable = table.querySelector("thead tr");
                var firstclm = table.querySelector('th[data-name="sequence"]');
                debugger;
                if (firstclm) {
                    firstclm.classList.add('custom-width');
                }
                if (childTable && !childTable.firstElementChild.classList.contains("o_list_row_count_sheliya")) {
                    var th = document.createElement("th");
                    th.className = "o_list_row_number_header o_list_row_count_sheliya";
                    th.style.width = "4%";
                    th.textContent = "#";
                    childTable.insertAdjacentElement('afterbegin', th);
                }
                var footer = table.querySelector("tfoot tr");
                if (footer && !footer.firstElementChild.classList.contains("o_list_row_count_sheliya")) {
                    var td = document.createElement("td");
                    td.className = "o_list_row_count_sheliya";
                    footer.insertAdjacentElement('afterbegin', td);
                }
                this.render();
            }
        });
    },
});