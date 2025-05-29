from odoo import http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.addons.website.controllers.main import Website
import werkzeug

class Books(http.Controller):
    def sitemap_books(env, rule, qs):
        books = env['library.book']
        dom = sitemap_qs2dom(qs, '/books', books._rec_name)
        for f in books.search(dom):
            loc = '/books/%s' % slug(f)
            if not qs or qs.lower() in loc:
                yield {'loc': loc}

    @http.route("/all-books", type='http', auth="none", website=True)
    def all_books(self, **kwargs):
        rs = request.env["library.book"].sudo()
        all_books = rs.search([])
        list_authors = rs.get_author_names(all_books)

        html_result = '<html><body><ul>'
        for book in all_books:
            html_result += "<li> %s </li>" % book.name + ' by ' + book.get_author_names(book)
        html_result += '</ul></body></html>'
        return html_result
        # return request.make_response(html_result, headers=[('Last-modified', email.utils.formatdate((fields.Datetime.from_string(rs.search([], order='write_date desc', limit=1).write_date) - datetime.datetime(1970, 1, 1)).total_seconds(), usegmt=True))])
        # return request.render("library_app.book_list_template", {"books": books, "authors": authors})

    @http.route('/all-books-json', type='json', auth='none')
    def all_books_json(self, **kwargs):
        rs = request.env['library.book'].sudo().search([])
        return rs.read(['name'])

    @http.route('/all-books/mark-mine', type='http', auth='public')
    def all_books_mark_mine(self, **kwargs):
        books = request.env['library.book'].sudo().search([])
        html_result = '<html><body><ul>'
        for book in books:
            if request.env.user.partner_id.id in book.author_ids.ids:
                html_result += "<li> %s </li> written by %s" % (book.name, request.env.user.partner_id.name)
            else:
                html_result += "<li> %s </li>" % book.name
        html_result += '</ul></body></html>'
        return html_result

    @http.route('/all-books/mine', type='http', auth='user')
    def all_books_mine(self, **kwargs):
        books = request.env['library.book'].search([
            ('author_ids', 'in', request.env.user.partner_id.ids),
        ])
        html_result = '<html><body><ul>'
        for book in books:
            html_result += "<li> %s </li>" % book.name
        html_result += '</ul></body></html>'
        return html_result

        # @http.route('/all-books/group_user', type='http', auth='base_group_user')
        # def all_books_mine_base_group_user(self):
        #     # your code
        #     return ''
        #
        # @http.route('/all-books/groups', type='http', auth='groups(base.group_no_one)')
        # def all_books_mine_groups(self):
        #     # your code
        #     return ''

    @http.route('/book_details', type='http', auth='user')
    def book_details(self, book_id, **kwargs):
        record = request.env['library.book'].sudo().browse(int(book_id))
        return u'<html><body><h1>%s</h1>Authors: %s' % (record.name, u', '.join(record.author_ids.mapped('name')) or 'none')

    @http.route('/book_details/<model("library.book"):book>', type='http', auth='user')
    def book_details_in_path(self, book, **kwargs):
        return self.book_details(book.id)

    @http.route('/demo_page', type='http', auth='user')
    def books(self, **kwargs):
        image_url = '/library_portal/static/src/image/logoslc.png'
        html_result = """<html>
                <body>
                    <img src="%s"/>
                </body>
            </html>""" % image_url
        return html_result

    @http.route('/books', type='http', auth="user", website=True)
    def library_books(self, **kwargs):
        # return request.render('library_portal.books', {'books': request.env['library.book'].search([])})
        country_id = False
        country_code = request.session.geoip and request.session.geoip.get('country_code') or False
        if country_code:
            country_ids = request.env['res.country'].sudo().search([('code', '=', country_code)])
            if country_ids:
                country_id = country_ids[0].id
        domain = ['|', ('restrict_country_ids', '=', False), ('restrict_country_ids', 'not in', [country_id])]
        domain += request.website.website_domain()
        return request.render('library_portal.books', {'books': request.env['library.book'].search(domain)})

    @http.route('/books/<model("library.book"):book>', type='http', auth="user", website=True, sitemap=sitemap_books)
    def library_book_detail(self, book, **post):
        if not book.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()
        return request.render('library_portal.book_detail', {'book': book, 'main_object': book })

    @http.route('/submit_issues', type='http', auth="user", website=True)
    def books_issues(self, **post):
        if post.get('book_id'):
            book_id = int(post.get('book_id'))
            issue_description = post.get('issue_description')
            request.env['book.issue'].sudo().create({
                'book_id': book_id,
                'issue_description': issue_description,
                'submitted_by': request.env.user.id
            })
            return request.redirect('/submit_issues?submitted=1')

        return request.render('library_portal.books_issue_form', {
            'books': request.env['library.book'].search([]),
            'submitted': post.get('submitted', False)
        })

    @http.route("/catalog", auth="public", website=True)
    def catalog(self, **kwargs):
        book = http.request.env["library.book"]
        books = book.sudo().search([])
        response = http.request.render("library_portal.catalog_template", {"books": books}, )
        return response


class WebsiteInfo(Website):
    @http.route()
    def website_info(self):
        result = super(WebsiteInfo, self).website_info()
        result.qcontext['apps'] = result.qcontext['apps'].filtered(lambda x: x.name != 'website')
        return result

