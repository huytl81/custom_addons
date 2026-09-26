# -*- coding: utf-8 -*-
import datetime
import logging
import pytz
from odoo.http import request

_logger = logging.getLogger(__name__)


def _is_true(val):
    if val is None or val is False:
        return False
    return str(val).strip().lower() in ('true', '1', 't', 'yes')


def get_params():
    default_bg = '/odoo_web_login/static/src/img/background_login_2.png'
    params = {
        'disable_footer': False,
        'disable_database_manager': False,
        'background_src': default_bg,
    }

    if not getattr(request, 'db', None):
        return params

    try:
        param_obj = request.env['ir.config_parameter'].sudo()
        params['disable_footer'] = _is_true(param_obj.get_param('login_form_disable_footer', 'False'))
        params['disable_database_manager'] = _is_true(param_obj.get_param('login_form_disable_database_manager', 'False'))
        change_background = _is_true(param_obj.get_param('login_form_change_background_by_hour', 'False'))

        if change_background:
            config_tz = param_obj.get_param('login_form_change_background_timezone', 'UTC')
            try:
                tz = pytz.timezone(config_tz)
            except Exception:
                tz = pytz.utc

            current_hour = datetime.datetime.now(tz=tz).hour

            if current_hour < 3 or current_hour >= 18:  # Night
                bg = param_obj.get_param('login_form_background_night')
            elif 3 <= current_hour < 7:  # Dawn
                bg = param_obj.get_param('login_form_background_dawn')
            elif 7 <= current_hour < 16:  # Day
                bg = param_obj.get_param('login_form_background_day')
            else:  # Dusk
                bg = param_obj.get_param('login_form_background_dusk')

            params['background_src'] = bg or default_bg
        else:
            params['background_src'] = param_obj.get_param('login_form_background_default') or default_bg
    except Exception as e:
        _logger.warning("Error loading odoo_web_login parameters: %s", e)

    return params