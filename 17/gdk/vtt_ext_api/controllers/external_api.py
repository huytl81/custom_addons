from odoo import http, api
from odoo.http import request
# from jose import jwt
# import jwt
from datetime import datetime, timedelta

SECRET_KEY = "94ffe5366a5afab7c5eaec411f24bf9c041a1524" # Thay thế bằng khóa bí mật của bạn

class AuthController(http.Controller):

    @http.route("/api/authex", methods=["POST"], auth='none', csrf=False)
    def auth(self, req):
        data = req.json()
        username = data.get("username")
        password = data.get("password")

        # Xác thực người dùng
        user = request.env["res.users"].sudo().authenticate(
            request.env.cr.dbname,
            username,
            password,
            request.httprequest.environ.get("HTTP_USER_AGENT"),
        )

        if not user:
            return req.make_response("Sai tên đăng nhập hoặc mật khẩu", 401)

        # Tạo token JWT
        payload = {
            "user_id": user.id,
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        # token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        token = ''
        return req.make_response({"access_token": token.decode("utf-8")})

    # @http.route("/api/invoices", methods=["GET"])
    # def invoices(self, req):
    #     # Lấy token từ header
    #     token = req.httprequest.headers.get("Authorization")
    #     if not token or not token.startswith("Bearer "):
    #         return req.make_response("Token không hợp lệ", 401)
    #
    #     # Giải mã token
    #     try:
    #         payload = jwt.decode(token[7:], SECRET_KEY, algorithms=["HS256"])
    #     except jwt.JWTError:
    #         return req.make_response("Token không hợp lệ", 401)
    #
    #     # Lấy thông tin người dùng từ payload
    #     user_id = payload.get("user_id")
    #     user = request.env["res.users"].sudo().browse(user_id)
    #
    #     # Lấy danh sách hóa đơn của người dùng
    #     invoices = request.env["account.move"].sudo().search([
    #         ("partner_id", "=", user.partner_id.id),
    #     ])
    #
    #     return req.make_response({"invoices": [i.id for i in invoices]})
