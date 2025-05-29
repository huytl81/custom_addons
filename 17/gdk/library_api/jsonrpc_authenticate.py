import json
import random
import requests


server_url = 'http://localhost:8017'
db_name = 'master'
username = 'admin'
password = 'admin'

json_endpoint = "%s/jsonrpc" % server_url
headers = {"Content-Type": "application/json"}


def get_json_payload(service, method, *args):
    return json.dumps({
        "jsonrpc": "2.0",
        "method": 'call',
        "params": {
            "service": service,
            "method": method,
            "args": args
        },
        "id": random.randint(0, 1000000000),
    })


payload = get_json_payload("common", "login", db_name, username, password)
response = requests.post(json_endpoint, data=payload, headers=headers)
js_result = response.json()
user_id = js_result['result']

if user_id:
    print("Success: userID is", user_id)
else:
    print("Failed: wrong credentials")