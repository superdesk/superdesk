define([
    'angular',
    'require',
    './dashboard-controller',
    './widget-service',
    './sd-widget-directive',
    './grid/grid',
    './world-clock/world-clock'
], function(angular, require) {
    'use strict';

    return angular.module('superdesk.dashboard', [
        'superdesk.dashboard.grid',
        'superdesk.dashboard.world-clock'
    ])

    .service('widgetService', require('./widget-service'))
    .directive('sdWidget', require('./sd-widget-directive'))

    .filter('wcodeFilter', function() {
        return function(input, values) {
            return _.pick(input, _.difference(_.keys(input), _.keys(values)));
        };
    })

    .config(['superdeskProvider', function(superdesk) {
        superdesk.activity('/dashboard', {
            label: gettext('Dashboard'),
            controller: require('./dashboard-controller'),
            templateUrl: require.toUrl('./views/dashboard.html'),
            priority: -1000,
            category: superdesk.MENU_MAIN
        });
    }]);
});
