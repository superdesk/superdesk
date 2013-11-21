define([
    'angular',
    'angular-route',
    'gridster',
    './controllers/main',
    './services',
    './directives',
    './filters',
    './widgets/worldClock/worldClock'
], function(angular) {
    'use strict';

    angular.module('superdesk.dashboard', [
        'ngRoute',
        'superdesk.userSettings',
        'superdesk.dashboard.services',
        'superdesk.dashboard.directives',
        'superdesk.dashboard.filters',
        'superdesk.widgets.worldClock'
    ])
    .constant('widgetsPath', 'scripts/superdesk-dashboard/widgets/')
    .config(function(menuProvider) {
        menuProvider.register({
            id: 'dashboard',
            label: gettext('Dashboard'),
            href: '/',
            priority: -1000,
            parentId: null
        });
    })
    .config(['$routeProvider', function($routeProvider) {
        $routeProvider
            .when('/', {
                controller: require('superdesk-dashboard/controllers/main'),
                templateUrl: 'scripts/superdesk-dashboard/views/main.html',
                resolve: {}
            });
    }]);
});
