/* @odoo-module */

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, markup, onMounted, xml } from "@odoo/owl";
import { escape, sprintf } from "@web/core/utils/strings";

export const simpleNotificationService = {
    dependencies: ["bus_service", "notification"],
    start(env, { bus_service, notification: notificationService }) {
        bus_service.subscribe("simple_notification_1", ({ message, sticky, title, type, links_u }) => {
            console.log('aaaaaaaaaaaaaaaaaaaa');
            console.log(links_u);
            // notificationService.add(message, { sticky, title, type });
            // useService('notification').add(
            //     "Message detail.", 
            //     { 
            //         title: "warning head", 
            //         type: "warning", 
            //         sticky: true
            //     }
            // );
            const options = {
                // className: params.className || "",
                sticky: sticky,
                title: title,
                type: 'warning',
            };
            const links = (links_u || []).map((link) => {
                return `<a href="${escape(link.url)}" target="_blank">${escape(link.label)}</a>`;
            });
            console.log(links);
            const html = markup(`${message} ${links}`);
            const messagec = markup(sprintf(escape(message), ...links));
            console.log(messagec);
            env.services.notification.add(html, options);
        });
        bus_service.start();
    },
};

registry.category("services").add("simple_notification_1", simpleNotificationService);

// // static/src/js/web_push.js

// import { useAutofocus, useService } from "@web/core/utils/hooks";

// odoo.define('sh_web_notification.web_push', function(require) {
//     "use strict";
//     // var core = require('web.core');
//     var rpc = useService("rpc");
//     // var _t = core._t;
//     function subscribeUser(pushSubscription) {
//         rpc.query({
//             model: 'sale.order',
//             method: 'store_subscription',
//             args: [pushSubscription],
//         });
//     }
//     if ('serviceWorker' in navigator) {
//         navigator.serviceWorker.register('/sh_web_notification/static/src/js/service-worker.js')
//             .then(function(registration) {
//                 return registration.pushManager.getSubscription()
//                     .then(function(subscription) {
//                         if (subscription) {
//                             return subscription;
//                         }
//                         return registration.pushManager.subscribe({
//                             userVisibleOnly: true,
//                             applicationServerKey: 'YOUR_PUBLIC_VAPID_KEY',
//                         });
//                     });
//             })
//             .then(function(subscription) {
//                 subscribeUser(subscription);
//             })
//             .catch(function(error) {
//                 console.error('Service Worker Error', error);
//             });
//     }
// });