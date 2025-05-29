import odoorpc

db_name = 'master'
username = 'admin'
password = 'admin'

# Prepare the connection to the server
orpc = odoorpc.ODOO('localhost', port=8017)
orpc.login(db_name, username, password)  # login

search_domain = ['|', ['name', 'ilike', 'odoo'], ['name', 'ilike', 'sql']]
books_info = orpc.execute('library.book', 'search_read',[search_domain], ['name', 'published_date'])
print(books_info)
