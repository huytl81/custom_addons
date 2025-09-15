import xmlrpc.client

url= 'http://localhost:8069'
username='admin'
password='admin'
db='odoo18'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
print(common.version())

uid = common.authenticate(db, username, password,{})
print(uid)

objects = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# search function
property_searched_ids = objects.execute_kw(db, uid, password, 'estate.property', 'search', [[]], {'offset': 2, 'limit': 3})
print("search function:", property_searched_ids)

# search_count function
property_counted = objects.execute_kw(db, uid, password, 'estate.property', 'search_count', [[]])
print("count function:", property_counted)

# search_read function
property_search_read_ids = objects.execute_kw(db, uid, password, 'estate.property', 'search_read', [[]], {'fields': ['id', 'name']})
print("search and read function:", property_search_read_ids)

# browse function -> Khong dung duoc trong XML-RPC
# property_browsed_ids = objects.execute_kw(db, uid, password, 'estate.property', 'browse', [[property_searched_ids[0], property_searched_ids[1]]])

# read function
property_read_ids = objects.execute_kw(db, uid, password, 'estate.property', 'read', [[property_searched_ids[0], property_searched_ids[1]]], {'fields':['id', 'name']})
print("read function:", property_read_ids)

records = objects.execute_kw(db, uid, password, 'estate.property', 'read', [[1, 2, 3, 5], ['display_name']])
for record in records:
    pairs = [(record['id'], record['display_name'])]
    my_id, my_name = [(record['id'], record['display_name'])]
    print(pairs)

# read_group function
property_read_group_ids = objects.execute_kw(db, uid, password, 'estate.property', 'read_group', [['selling_price', '>' , 0]],  ['type_id', 'selling_price:sum'], ['type_id'])
print("read group function:", property_read_group_ids)

# create function
property_created_id = objects.execute_kw(db, uid, password, 'estate.property', 'create', [{'name': 'New Property from XMLRPC','type_id': 1, 'seller_id': 6}])
print("create function:", property_created_id)

# write function
# property_write_id = objects.execute_kw(db, uid, password, 'estate.property', 'write', [[property_created_id], {'name': 'New Property from XMLRPC 2'}])
property_is_written = objects.execute_kw(db, uid, password, 'estate.property', 'write', [[13], {'name': 'New Property from XMLRPC 2'}])
print("write function:", property_is_written)

# update function
property_is_updated = objects.execute_kw(db, uid, password, 'estate.property', 'update', [[13], {'name': 'New Property from XMLRPC 2'}])
print("update function:", property_is_updated)

# unlink function
property_is_unlink = objects.execute_kw(db, uid, password, 'estate.property', 'unlink', [[12]])
print("unlink function:", property_is_unlink)
