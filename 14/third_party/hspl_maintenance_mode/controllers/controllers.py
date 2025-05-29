# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.web.controllers.main import Home
from odoo.addons.website.controllers.main import Website
from odoo.http import request


class HsplMaintenanceHome(Home):

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        maintenance_mode = request.env['ir.config_parameter'].sudo().get_param('hspl.maintenance_mode', False)
        maintainer_user_ids = request.env.ref('base.group_system').sudo().users.ids
        is_maintainer = True if request.session.uid in maintainer_user_ids else False
        if bool(maintenance_mode) and not is_maintainer:
            company_id = request.env.user.company_id if request.env.user.company_id else request.env.ref(
                'base.main_company')
            return request.render('hspl_maintenance_mode.under_maintenance',
                                  {'res_company': company_id})
        return super(HsplMaintenanceHome, self).web_client(s_action, **kw)


class HsplMaintenanceWebsite(Website):

    @http.route('/', type='http', auth="public", website=True)
    def index(self, **kw):
        maintenance_mode = request.env['ir.config_parameter'].sudo().get_param('hspl.maintenance_mode', False)
        maintainer_user_ids = request.env.ref('base.group_system').sudo().users.ids
        is_maintainer = True if request.session.uid in maintainer_user_ids else False
        if bool(maintenance_mode) and not is_maintainer:
            company_id = request.env.user.company_id if request.env.user.company_id else request.env.ref(
                'base.main_company')
            return request.render('hspl_maintenance_mode.under_maintenance',
                                  {'res_company': company_id})
        return super(HsplMaintenanceWebsite, self).index(**kw)
