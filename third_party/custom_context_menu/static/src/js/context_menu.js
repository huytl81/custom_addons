/** @odoo-module **/
import { App } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";
import { useService } from "@web/core/utils/hooks";
import { ContextMenu } from "./ContextMenu";
import { getTemplate } from "@web/core/templates" ;
import { session } from "@web/session";

patch(WebClient.prototype, {

    async setup() {
        super.setup();
        if(session?.contextmenu_enabled) {
            this.menuService = useService("menu");
            this.odooMenus = await this.menuService.getApps().map(menu => this.menuService.getMenuAsTree(menu.id))
            $(document).on('contextmenu', this.showContextMenu.bind(this));
            $(document).on('click', function () { $('.cm_container').length ? $('.cm_container').remove() : null });
        }
    },

    showContextMenu(e) {
        e.preventDefault();
        $('.cm_container').length ? $('.cm_container').remove() : null
        $('body').append($('<div>', {class: 'cm_container'}));
        const app = new App(ContextMenu, { getTemplate, props: {items: this.odooMenus}});
        app.mount($('.cm_container')[0]).then(() => {
            var menu = $('.cm_container'), mouseX = e.clientX, mouseY = e.clientY, offset = 5;
            var menuWidth = menu.outerWidth(), menuHeight = menu.outerHeight();
            var winWidth = $(window).width(), winHeight = $(window).height();
            let left = (mouseX + offset + menuWidth) > winWidth ? winWidth - menuWidth - offset : mouseX + offset;
            let top = (mouseY + offset + menuHeight) > winHeight ? winHeight - menuHeight - offset : mouseY + offset;
            menu.css({ top: top + 'px', left: left + 'px'}).addClass('display');
        })
    },
});