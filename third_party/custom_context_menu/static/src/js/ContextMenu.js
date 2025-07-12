/** @odoo-module **/
import { Component } from "@odoo/owl";

export class ContextMenu extends Component {
    static template = "ContextMenu";
    static components = { ContextMenu };
    static props = {items: Array,};

    setup() {
        super.setup(...arguments);
        this.currentZIndex = 10000;
    }

    openSubmenu(e) {
        const $submenu = $(e.currentTarget).find('>#context_menu');
        if (!$submenu.length) return;
        const submenuWidth = $submenu.outerWidth(), submenuHeight = $submenu.outerHeight();
        const parentWidth = $(e.currentTarget).outerWidth(), parentOffset = $(e.currentTarget).offset();
        const windowWidth = $(window).width(), windowHeight = $(window).height();
        let left = parentOffset.left + parentWidth + submenuWidth > windowWidth ? -submenuWidth : parentWidth;
        let top = parentOffset.top + submenuHeight > windowHeight ? windowHeight - parentOffset.top - submenuHeight - 10 : 0;
        $(e.currentTarget).css({ zIndex: this.currentZIndex });
        $submenu.css({ top: top + 'px', left: left + 'px', zIndex: this.currentZIndex++ });
    }

    prepareUrl(item) {
        return '/odoo/' + (item.actionPath ? item.actionPath : 'action-'+item.actionID);
    }
} 