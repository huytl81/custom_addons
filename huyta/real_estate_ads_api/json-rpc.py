import urllib.request
import random
import json


url= 'http://localhost:8069'
username='admin'
password='admin'
db='odoo18'

def json_rpc(url, method, params):
    data = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": random.randint(0, 10000000000)
    }

    headers = {
        "Content-Type": "application/json"
    }

    request = urllib.request.Request(url=url, data=json.dumps(data).encode(), headers=headers)
    response = json.loads(urllib.request.urlopen(request).read().decode("UTF-8"))

    if response.get("error"):
        raise Exception(response["error"])
    return response["result"]

def call(url, service, method, *args):
    return json_rpc(f"{url}/jsonrpc", "call", params={"service": service, "method": method, "args": args})

authenticated_id = call(url, "common", "login", db, username, password)
print(authenticated_id)

vals = {
    "name": "Real Estate Property from JSON",
    "seller_id": 6,
    "type_id": 3
}

# property_created_id = call(url, "object", "execute", db, authenticated_id, password, "estate.property", "create", [vals])
# print("create function:", property_created_id)

property_read_id = call(url, "object", "execute", db, authenticated_id, password, "estate.property", "read", [14])
print("read function:", property_read_id)

property_read_group_ids = call(url, "object", "execute", db, authenticated_id, password, "estate.property", "read_group", [['selling_price', '>' , 0]],  ['type_id', 'selling_price:sum'], ['type_id'])
print("read group function:", property_read_group_ids)