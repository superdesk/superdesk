define(['lodash'], function(_) {
    'use strict';

    function WidgetsProvider() {

        var widgets = {};

        this.widget = function(id, widget) {
            widgets[id] = _.extend({_id: id}, widget);
        };

        this.$get = function() {
            return _.values(widgets);
        };
    }

    return WidgetsProvider;
});
