# -*- coding: utf-8 -*-

from odoo import _
from odoo.addons.portal.controllers import portal
from odoo.http import request
from odoo.exceptions import UserError


class CustomerPortal(portal.CustomerPortal):

    def _show_report(self, model, report_type, report_ref, download=False):
        ReportAction = request.env['ir.actions.report'].sudo()
        r = request.env.ref(report_ref)
        if r.report_type == 'py3o':
            if report_type not in ('html', 'pdf', 'text'):
                raise UserError(_("Invalid report type: %s", report_type))

            if hasattr(model, 'company_id'):
                if len(model.company_id) > 1:
                    raise UserError(_('Multi company reports are not supported.'))
                ReportAction = ReportAction.with_company(model.company_id)

            method_name = '_render_py3o'
            report = getattr(ReportAction, method_name)(report_ref, list(model.ids), data={'report_type': report_type})[
                0]
            headers = self._get_http_headers(model, report_type, report, download)

            return request.make_response(report, headers=list(headers.items()))

        else:
            return super()._show_report(model, report_type, report_ref, download)