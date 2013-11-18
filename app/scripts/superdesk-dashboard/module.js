define([
    'angular',
    'angular-route',
    'gridster',
    './controllers/main',
    './services',
    './directives',
    './filters',
    './widgets/worldClock/worldClock',
    './widgets/ingest/ingest'
], function(angular) {
    'use strict';

    angular.module('superdesk.dashboard', [
        'ngRoute',
        'superdesk.userSettings',
        'superdesk.dashboard.services',
        'superdesk.dashboard.directives',
        'superdesk.dashboard.filters',
        'superdesk.widgets.worldClock',
        'superdesk.widgets.ingest'
    ])
    .constant('widgetsPath', 'scripts/superdesk-dashboard/widgets/')
    .config(['$routeProvider', function($routeProvider) {
        $routeProvider
            .when('/', {
                controller: require('superdesk-dashboard/controllers/main'),
                templateUrl: 'scripts/superdesk-dashboard/views/main.html',
                resolve: {},
                menu: {
                    label: 'Dashboard',
                    priority: -1000
                }
            });
    }]);
});
