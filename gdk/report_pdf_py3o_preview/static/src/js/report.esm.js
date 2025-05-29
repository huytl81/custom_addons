/** @odoo-module **/

import {WARNING_MESSAGE, WKHTMLTOPDF_MESSAGES, _getReportUrl} from "./tools.esm";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {download} from "@web/core/network/download";

/* eslint-disable init-declarations */
let wkhtmltopdfStateProm;
registry
    .category("ir.actions.report handlers")
    .add("open_report_handler", async function (action, options, env) {
        if (action.type === "ir.actions.report" && action.report_type === "qweb-pdf") {
            // Check the state of wkhtmltopdf before proceeding
            if (!wkhtmltopdfStateProm) {
                wkhtmltopdfStateProm = env.services.rpc("/report/check_wkhtmltopdf");
            }
            const state = await wkhtmltopdfStateProm;
            if (state in WKHTMLTOPDF_MESSAGES) {
                env.services.notification.add(WKHTMLTOPDF_MESSAGES[state], {
                    sticky: true,
                    title: _t("Report"),
                });
            }
            if (state === "upgrade" || state === "ok") {
                // Trigger the download of the PDF report
                const url = _getReportUrl(action, "pdf", env);
                // AAB: this check should be done in get_file service directly,
                // should not be the concern of the caller (and that way, get_file
                // could return a deferred)
                if (!window.open(url)) {
                    env.services.notification.add(WARNING_MESSAGE, {
                        type: "warning",
                    });
                }
            }
            return Promise.resolve(true);
        }
        return Promise.resolve(false);
    });

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
            console.log(action);
            if (action.py3o_filetype === "pdf") {
                const url = _getReportUrl(action, "py3o", env);
                if (!window.open(url)) {
                    env.services.notification.add(WARNING_MESSAGE, {
                        type: "warning",
                    });
                }
                return Promise.resolve(true);
            }

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
    }, {force: true});
