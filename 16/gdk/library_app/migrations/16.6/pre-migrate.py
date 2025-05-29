
def migrate(cr, version):
    cr.execute('ALTER TABLE library_book RENAME COLUMN date_published TO date_published_char')
