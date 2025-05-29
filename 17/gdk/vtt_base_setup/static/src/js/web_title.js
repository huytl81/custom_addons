/** @odoo-module **/

import { registry } from "@web/core/registry";
import { WebClient } from "@web/webclient/webclient"
import {patch} from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

// Replaces Odoo in window title to My Title
patch(WebClient.prototype,  {
    setup() {
        super.setup();
        const titleService = useService("title");
        var brand_title = session.brand_title;
        titleService.setParts({ zopenerp: brand_title });
    },
});