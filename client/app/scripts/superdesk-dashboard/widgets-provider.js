(function() {
    'use strict';

    angular.module('superdesk.dashboard.widgets', [])
    .provider('dashboardWidgets', function() {

        var privateWidgets = {};

        this.addWidget = function(id, widget, debug) {
            privateWidgets[id] = _.extend({_id: id}, widget);
        };

        this.$get = function() {
            return _.values(privateWidgets);
        };
    });

})();
