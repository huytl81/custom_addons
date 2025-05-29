import xmlrpc

from odoo import models


def main(self):
    url = 'http://localhost:8069'
    db = 'odoo15EE'
    username = 'admin'
    password = 'admin'
    info = xmlrpc.ServerProxy('https://localhost:8089/start').start()
    url, db, username, password = info['host'], info['database'], info['user'], info['password']
    uid = self.env.ref('base.user_admin').id

    models.execute_kw(db, uid, password,'sale.order', 'search',[('x_rush','=',True),('state','=','sale')])
    models.execute_kw(db, uid, password,'sale.order', 'search_read',[('x_rush','=',True),('state','=','done')],{'fields': ['name', 'country_id', 'comment'], 'limit': 5})