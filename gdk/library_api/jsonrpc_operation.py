import json
import random
import requests


server_url = 'http://localhost:8017'
db_name = 'master'
username = 'admin'
password = 'admin'

json_endpoint = "%s/jsonrpc" % server_url
headers = {"Content-Type": "application/json"}


def get_json_payload(service, method, *args, **kwargs):
    kwargs = kwargs or {}
    return json.dumps({
        "jsonrpc": "2.0",
        "method": 'call',
        "params": {
            "service": service,
            "method": method,
            "args": args,
            "kwargs": kwargs
        },
        "id": random.randint(0, 1000000000),
    })


payload = get_json_payload("common", "login", db_name, username, password)
response = requests.post(json_endpoint, data=payload, headers=headers)
user_id = response.json()['result']

if user_id:
    # creates the books records
    create_data = [
        {'name': 'Book 1', 'published_date': '2019-01-26'},
        {'name': 'Book 3', 'published_date': '2019-02-12'},
        {'name': 'Book 5', 'published_date': '2019-05-08'},
        {'name': 'Book 7', 'published_date': '2019-05-14'}
    ]
    payload = get_json_payload("object", "execute_kw", db_name, user_id, password, 'library.book', 'create', [create_data])
    res = requests.post(json_endpoint, data=payload, headers=headers).json()
    print("Books created:", res)
    books_ids = res['result']

    # Write in existing book record
    book_to_write = books_ids[1]  # We will use ids of recently created books
    write_data = {'name': 'Book 2'}
    payload = get_json_payload("object", "execute_kw", db_name, user_id, password, 'library.book', 'write', [book_to_write, write_data])
    res = requests.post(json_endpoint, data=payload, headers=headers).json()
    if res['result']:
        payload = get_json_payload("object", "execute_kw", db_name, user_id, password, 'library.book', 'browse', [int(book_to_write), ['name']])
        response = requests.post(json_endpoint, data=payload, headers=headers).json()
        print("Books written:", response['result'][0])

    # Delete in existing book record
    book_to_unlink = books_ids[2:]  # We will use ids of recently created books
    payload = get_json_payload("object", "execute_kw", db_name, user_id, password, 'library.book', 'unlink', [book_to_unlink])
    res = requests.post(json_endpoint, data=payload, headers=headers).json()
    print("Books deleted:", res['result'])

else:
    print("Failed: wrong credentials")