/** @odoo-module **/
import { Chatter } from "@mail/chatter/web_portal/chatter";
import { patch } from "@web/core/utils/patch";
import { ControlPanel } from "@web/search/control_panel/control_panel";
import { _t } from "@web/core/l10n/translation";
import { rpc } from '@web/core/network/rpc';

patch(Chatter.prototype, {  
    
    async setup() {
        super.setup(...arguments);
        console.log("Chatter setup called");  
        this.toggleChatterVisibility();
    },

    async toggleChatterVisibility() {
        try {
           
            const userSpecificData = await rpc("/web/dataset/call_kw/res.users/get_chatter_toggle_flag", {
                model: "res.users",
                method: "get_chatter_toggle_flag",
                args: [],
                kwargs: {},
            });
            const groupSpecificData = await rpc("/web/dataset/call_kw/res.users/get_chatter_toggle_group_flag", {
                model: "res.users",
                method: "get_chatter_toggle_group_flag",
                args: [],
                kwargs: {},
            });


            const chatterToggleButton = document.getElementById("chatter-toggle");
            const chatToggleButton = document.getElementById("toggleChatButton");
    
            const isChatterEnabled = userSpecificData.enable_chatter_button === 1 || groupSpecificData.enable_chatter_group === 1;
    
            if (isChatterEnabled) {
                if (chatterToggleButton) chatterToggleButton.classList.add("chatter-visible");
                if (chatToggleButton) chatToggleButton.classList.add("chatter-visible");
            }
        } catch (error) {
            console.error("Error toggling chatter visibility:", error);
        }
    },

    toggleChatter() {
        const chatterElement = document.querySelector('.o-mail-ChatterContainer');
        const showChatterButton = document.querySelector('#history_btn'); 
        const hideChatterButton = document.querySelector('button[title="Hide Chatter"]'); 
    
        
        if (chatterElement) {
            chatterElement.classList.add('d-none'); 
        }
    
        
        if (hideChatterButton) {
            hideChatterButton.classList.add('d-none'); 
        }
    
        if (showChatterButton) {
            showChatterButton.classList.remove('d-none'); 
        }
    }      
    ,    
    toggleChat() {
        const chatterElement = document.querySelector('.o-mail-Thread');
        const toggleIcon = document.querySelector('#chatterToggleIcon'); 
        const toggleButton = document.querySelector('#toggleChatButton');
    
        if (chatterElement) {
           
            chatterElement.classList.toggle('d-none');
    
            if (toggleIcon) {
              
                if (chatterElement.classList.contains('d-none')) {
                   
                    toggleIcon.classList.remove('fa-eye-slash');
                    toggleIcon.classList.add('fa-eye');
                    toggleButton.title = "Show Chat";
                } else {
                   
                    toggleIcon.classList.remove('fa-eye');
                    toggleIcon.classList.add('fa-eye-slash');
                    toggleButton.title = "Hide Chat";
                }
            } else {
                console.error("Chatter toggle icon not found!");
            }
        } else {
            console.error("Chatter element not found!");
        }
    }
    
    
});

patch(ControlPanel.prototype, {   
    toggleChattershow() {
    
        const chatterElement = document.querySelector('.o-mail-ChatterContainer');
        const showChatterButton = document.querySelector('#history_btn'); 
        const hideChatterButton = document.querySelector('button[title="Hide Chatter"]'); 
    
        
        if (chatterElement) {
            chatterElement.classList.remove('d-none'); 
        }
    
       
        if (showChatterButton) {
            showChatterButton.classList.add('d-none'); 
        }
    
        
        if (hideChatterButton) {
            hideChatterButton.classList.remove('d-none'); 
        }
    }
});