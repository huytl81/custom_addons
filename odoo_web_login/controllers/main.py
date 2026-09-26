# -*- encoding: utf-8 -*-
##############################################################################
#
#    Samples module for Odoo Web Login Screen
#    Copyright (C) 2017- XUBI.ME (http://www.xubi.me)
#    @author binhnguyenxuan (https://www.linkedin.com/in/binhnguyenxuan)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#    
#
##############################################################################

import logging
from odoo import http
from odoo.addons.web.controllers.home import Home
from ..utilities import get_params

_logger = logging.getLogger(__name__)

try:
    from odoo.addons.auth_signup.controllers.main import AuthSignupHome
except ImportError:
    AuthSignupHome = Home


# ----------------------------------------------------------
# Odoo Web web Controllers
# ----------------------------------------------------------
class LoginHome(Home):
    @http.route()
    def web_login(self, *args, **kw):
        if getattr(http.request, 'db', None):
            try:
                website_layout = http.request.env.ref('website.login_layout', raise_if_not_found=False)
                if website_layout and website_layout.active:
                    website_layout.sudo().write({'active': False})
            except Exception:
                pass
        response = super().web_login(*args, **kw)
        if hasattr(response, 'qcontext'):
            response.qcontext.update(get_params())
        return response


class OdooWebLoginSignup(AuthSignupHome):
    @http.route()
    def web_auth_signup(self, *args, **kw):
        response = super().web_auth_signup(*args, **kw)
        if hasattr(response, 'qcontext'):
            response.qcontext.update(get_params())
        return response
