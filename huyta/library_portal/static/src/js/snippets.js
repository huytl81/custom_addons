odoo.define('book.dynamic.snippet', function (require) {
    'use strict';

    let publicWidget = require('web.public.widget');
    publicWidget.registry.books = publicWidget.Widget.extend({
        selector: '.book_snippet',
        disabledInEditableMode: false,
        start: function () {
            var self = this;
            var rows = this.$el[0].dataset.numberOfBooks || '5';
            this.$el.find('td').parents('tr').remove();
            this._rpc({
                model: 'library.book',
                method: 'search_read',
                domain: [],
                fields: ['name', 'published_date'],
                orderBy: [{
                    name: 'published_date', asc: false
                }],
                limit: parseInt(rows)
            }).then(function (data) {
                _.each(data, function (book) {
                    self.$el.append(
                        $('<tr />').append(
                            $('<td />').text(book.name),
                            $('<td />').text(book.published_date)
                        ));
                });
            });
        },
    });
});