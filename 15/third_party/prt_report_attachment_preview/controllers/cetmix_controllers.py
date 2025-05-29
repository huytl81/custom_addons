###################################################################################
# 
#    Copyright (C) Cetmix OÜ
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

import json

from odoo import http
from odoo.http import request
from odoo.tools.safe_eval import safe_eval, time

from odoo.addons.http_routing.models.ir_http import slugify
from odoo.addons.web.controllers.main import ReportController


class CxReportController(ReportController):
    def _prepare_filepart(self, doc_ids, report):
        """Prepare filename for report"""
        if doc_ids:
            doc_ids_len = len(doc_ids)
            if doc_ids_len > 1:
                model_id = request.env["ir.model"]._get(report.model)
                return "{} (x{})".format(model_id.name, doc_ids_len)
            report_name = report.print_report_name
            if doc_ids_len == 1 and report_name:
                obj = request.env[report.model].browse(doc_ids)
                return safe_eval(report_name, {"object": obj, "time": time})
        return "report"

    @http.route(
        [
            "/report/<converter>/<reportname>",
            "/report/<converter>/<reportname>/<docids>",
        ],
        type="http",
        auth="user",
        website=True,
    )
    def report_routes(self, reportname, docids=None, converter=None, **data):
        """
        Overwrite method to open PDF report in new window
        """
        if converter != "pdf":
            return super().report_routes(
                reportname, docids=docids, converter=converter, **data
            )
        report = request.env["ir.actions.report"]._get_report_from_name(reportname)
        context = dict(request.env.context)
        if docids:
            docids = [int(i) for i in docids.split(",")]
        if data.get("options"):
            data.update(json.loads(data.pop("options")))
        if data.get("context"):
            data["context"] = json.loads(data["context"])
            context.update(data["context"])
        # Get filename for report
        filepart = self._prepare_filepart(docids, report)
        pdf = report.with_context(**context)._render_qweb_pdf(docids, data=data)[0]
        return request.make_response(
            pdf,
            headers=[
                ("Content-Type", "application/pdf"),
                ("Content-Length", len(pdf)),
                (
                    "Content-Disposition",
                    'inline; filename="%s.pdf"' % slugify(filepart),
                ),
            ],
        )
