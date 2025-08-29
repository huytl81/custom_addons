odoo.define('my_field_widget', function (require) {
    "use strict";

    const { Component } = owl;
    const AbstractField = require('web.AbstractFieldOwl');
    const fieldRegistry = require('web.field_registry_owl');

    class ColorPill extends Component {
        static template = 'OWLColorPill';
        pillClicked() {
            this.trigger('color-updated', {val: this.props.pill_no});
        }
    }

    class FieldColor extends AbstractField {
        static supportedFieldTypes = ['integer'];
        static template = 'OWLFieldColorPills';
        static components = { ColorPill };

        constructor(...args) {
            super(...args);
            this.totalColors = Array.from({length: 10}, (_, i) => (i + 1).toString());
        }
        async willStart() {
            this.colorGroupData = {};
            var colorData = await this.rpc({
                model: this.model, method: 'read_group',
                domain: [], fields: ['color'],
                groupBy: ['color'],
            });
            colorData.forEach(res => {
                this.colorGroupData[res.color] = res.color_count;
            });
        }
        colorUpdated(ev) {
            this._setValue(ev.detail.val);
        }
    }

    fieldRegistry.add('int_color', FieldColor);

    return {
        FieldColor: FieldColor,
    };
});

// odoo.define('my_field_widget', function (require) {
//     "use strict";
//
//     var AbstractField = require('web.AbstractField');
//     var fieldRegistry = require('web.field_registry');
//
//     var core = require('web.core');
//
//     var qweb = core.qweb;
//
//
//     var colorField = AbstractField.extend({
//         className: 'o_int_colorpicker',
//         tagName: 'span',
//         supportedFieldTypes: ['integer'],
//         events: {
//             'click .o_color_pill': 'clickPill',
//         },
//         init: function () {
//             this.totalColors = 10;
//             this._super.apply(this, arguments);
//         },
//
//         willStart: function () {
//             var self = this;
//             this.colorGroupData = {};
//             var colorDataPromise = this._rpc({
//                 model: this.model,
//                 method: 'read_group',
//                 domain: [],
//                 fields: ['color'],
//                 groupBy: ['color'],
//             }).then(function (result) {
//                 _.each(result, function (r) {
//                     self.colorGroupData[r.color] = r.color_count;
//                 });
//             });
//             return Promise.all([this._super.apply(this, arguments), colorDataPromise]);
//         },
//
//         _renderEdit: function () {
//             this.$el.empty();
//             var pills = qweb.render('FieldColorPills', {widget: this});
//             this.$el.append(pills);
//             /*for (let i = 0; i < this.totalColors; i++) {
//                 let className = "o_color_pill o_color_" + i;
//                 if (this.value === i) {
//                     className += ' active';
//                 }
//                 this.$el.append($('<span>', {
//                     'class': className,
//                     'data-val': i,
//                 }));
//             }*/
//             this.$el.find('[data-toggle="tooltip"]').tooltip();
//         },
//
//         _renderReadonly: function () {
//             var className = "o_color_pill active readonly o_color_" + this.value;
//             this.$el.append($('<span>', {
//                 'class': className,
//             }));
//         },
//         clickPill: function (ev) {
//             var $target = $(ev.currentTarget);
//             var data = $target.data();
//             this._setValue(data.val.toString());
//         }
//
//     });
//
//     fieldRegistry.add('int_color', colorField);
//
//     return {
//         colorField: colorField,
//     };
// });