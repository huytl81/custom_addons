/** @odoo-module **/

import {download} from "@web/core/network/download";
import {registry} from "@web/core/registry";

registry
    .category("ir.actions.report handlers")
    .add("py3o_handler", async function (action, options, env) {

        function isUndefined(o) {
            return typeof o === "undefined";
          }

        function isNull(arg) {
          return arg === null;
        }

        function isObject(value) {
            return _typeof(value) === 'object' && value !== null;
        }

        function isEmpty(value) {
            return value === null || value === undefined;
        }

        if (action.report_type === "py3o") {
            let url = `/report/py3o/${action.report_name}`;
            const actionContext = action.context || {};
            if (
                isUndefined(action.data) ||
                isNull(action.data) ||
                (isObject(action.data) && isEmpty(action.data))
            ) {
                // Build a query string with `action.data` (it's the place where reports
                // using a wizard to customize the output traditionally put their options)
                if (actionContext.active_ids) {
                    var activeIDsPath = "/" + actionContext.active_ids.join(",");
                    url += activeIDsPath;
                }
            } else {
                var serializedOptionsPath =
                    "?options=" + encodeURIComponent(JSON.stringify(action.data));
                serializedOptionsPath +=
                    "&context=" + encodeURIComponent(JSON.stringify(actionContext));
                url += serializedOptionsPath;
            }
            env.services.ui.block();
            try {
                await download({
                    url: "/report/download",
                    data: {
                        data: JSON.stringify([url, action.report_type]),
                        context: JSON.stringify(env.services.user.context),
                    },
                });
            } finally {
                env.services.ui.unblock();
            }
            const onClose = options.onClose;
            if (action.close_on_report_download) {
                return env.services.action.doAction(
                    {type: "ir.actions.act_window_close"},
                    {onClose}
                );
            } else if (onClose) {
                onClose();
            }
            return Promise.resolve(true);
        }
        return Promise.resolve(false);
    });
