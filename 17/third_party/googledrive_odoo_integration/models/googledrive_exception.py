#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

class GoogleDriveRestApiError(Exception):
	"""Generic Googledrive Api error class

	To catch these, you need to import it in you code e.g. :
	from odoo.addons.googledrive_odoo_integration.models import googledrive_exception
	from odoo.addons.googledrive_odoo_integration.models.googledrive_exception import GoogleDriveRestApiError
	"""

	def __init__(self, msg, error_code=None, so_error_message='', so_error_code=None):
		self.msg = msg
		self.error_code = error_code
		self.so_error_message = so_error_message
		self.so_error_code = so_error_code

	def __str__(self):
		message=''
		if self.error_code==401:
			message='Code 401- Invalid Google Drive Oauth2 Information'
		message=message+repr(self.so_error_message)
		return message

class GoogleDriveResyncError(GoogleDriveRestApiError):
	'''
		Generic GoogleDriveResyncError error class
		This Class Inherits GoogleDriveRestApiError Class And Will Use When Access Token Will Expire
	'''
	pass