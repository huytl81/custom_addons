import requests
import json

# URL API
BASE_URL = "http://localhost:8084"

resss = requests.get('http://localhost:8084/api/tect')
ress = requests.get(f'{BASE_URL}/api/tect')

# csrf_token = requests.csrf_token()

# Lấy token
headers = {
    "Content-Type": "application/json",
    # "Authorization": f"Bearer {csrf_token}",
}
data = {"username": "admin", "password": "123"}
response = requests.post(f"{BASE_URL}/api/authex", headers=headers, data=json.dumps(data))

if response.status_code == 200:
    token = response.json().get("access_token")

    # Lấy danh sách hóa đơn
    headers["Authorization"] = f"Bearer {token}"
    response = requests.get(f"{BASE_URL}/api/invoices", headers=headers)

    if response.status_code == 200:
        invoices = response.json().get("invoices")
        print(f"Danh sách hóa đơn: {invoices}")
    else:
        print(f"Lỗi lấy danh sách hóa đơn: {response.text}")
else:
    print(f"Lỗi đăng nhập: {response.text}")


