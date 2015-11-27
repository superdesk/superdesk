(function() {
    'use strict';

    angular.module('superdesk.dashboard.widgets', [])
    .provider('widgets', function() {

        var widgets = {};

        this.widget = function(id, widget) {
            widgets[id] = _.extend({_id: id}, widget);
        };

        this.$get = function() {
            return _.values(widgets);
        };
    });

})();
