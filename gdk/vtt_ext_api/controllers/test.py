import requests
import json

# URL API
BASE_URL = "http://localhost:8084"

# resss = requests.get('http://localhost:8084/api/tect')
ress = requests.get(f'{BASE_URL}/api/toat')
dataAuth = {
    "jsonrpc": "2.0",
    "params": {
        "db": "test_17",
        "username": "admin",
        "password": "123"
    }
}
headers1 = {
    "Content-Type": "application/json",
    # "Authorization": f"Bearer {csrf_token}",
}
ress = requests.post(f'{BASE_URL}/vtt/api/authenticate', headers=headers1, data=dataAuth)

# csrf_token = requests.csrf_token()

# Lấy token
headers = {
    "Content-Type": "application/json",
    # "Authorization": f"Bearer {csrf_token}",
}
# data = {"username": "admin", "password": "123"}
data = {
    "jsonrpc": "2.0",
    "params": {
        "username": "123",
        "password": "123",
        "za_token": "",
    }
}
response = requests.post(f"{BASE_URL}/vtt/api/zalo_register", data=json.dumps(data))

if response.status_code == 200:
    abc = ''
    # token = response.json().get("access_token")
    #
    # # Lấy danh sách hóa đơn
    # headers["Authorization"] = f"Bearer {token}"
    # response = requests.get(f"{BASE_URL}/api/invoices", headers=headers)
    #
    # if response.status_code == 200:
    #     invoices = response.json().get("invoices")
    #     print(f"Danh sách hóa đơn: {invoices}")
    # else:
    #     print(f"Lỗi lấy danh sách hóa đơn: {response.text}")
else:
    print(f"Lỗi đăng nhập: {response.text}")


