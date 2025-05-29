from odoo import api, fields, models

class VttZaloNews(models.Model):
    _name = "vtt.zalo.news"

    # + Title: text
    # + Desciption: text
    # + Publish
    # date: datetime
    # + Author: text
    # + Article
    # Image: url

    title = fields.Char(string='Title')
    is_hot_news = fields.Boolean("Hot news", default=False)
    description = fields.Html('Content')
    publish_date = fields.Datetime(string='Publish date')
    author = fields.Char(string='Author')
    image = fields.Image('Image', store=True)
    public_link = fields.Char(string='Public link')
