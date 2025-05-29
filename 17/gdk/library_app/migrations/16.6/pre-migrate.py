
def migrate(cr, version):
    cr.execute('ALTER TABLE library_book RENAME COLUMN published_date TO published_date_char')
