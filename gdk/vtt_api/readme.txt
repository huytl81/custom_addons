1. Authenticate
- authen url:		http://127.0.0.1:8069/web/session/authenticate			thay host tương ứng
- authen type:		POST
- authen data:		{"jsonrpc": "2.0", "params": {"db": "tmt04", "login": "huubv", "password": "123"}}
- authen header:	{"Content-Type": "application/json"}

2. Get list api
- get list url:		http://127.0.0.1:8069/ev/api/demolistpost
- type:			POST
- data:			{"jsonrpc": "2.0", "parameters": {"model": "res.partner"}}		thay model theo nhu cầu
- header:
	>> sdung postman:	{"Content-Type": "application/json", "X-Openerp": session_id}
									session_id lấy từ authenticate response body
	>> sdung requests:	{"Content-Type": "application/json", "X-Openerp-Session-Id": session_id}
									session_id lấy từ Set-Cookie trong authenticate response headers
