import odoorpc

db_name = 'master'
username = 'admin'
password = 'admin'

# Prepare the connection to the server
orpc = odoorpc.ODOO('localhost', port=8017)
orpc.login(db_name, username, password)  # login

# User information
user = orpc.env.user
print(user.name)             # name of the user connected
print(user.company_id.name)  # the name of user's company
print(user.email)            # the email of usser

book_model = orpc.env['library.book']
search_domain = ['|', ['name', 'ilike', 'odoo'], ['name', 'ilike', 'sql']]
books_ids = book_model.search(search_domain, limit=5)
for book in book_model.browse(books_ids):
    print(book.name, book.published_date)

# create the book and update the state
book_id = book_model.create({'name': 'Odoo RPC Essential', 'state': 'draft'})
print("Book state before make_available:", book.state)
book = book_model.browse(book_id)
book.make_available()
book = book_model.browse(book_id)
print("Book state before make_available:", book.state)