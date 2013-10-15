define([
    'angular',
    'angular-route',
    'gridster',
    './controllers/main',
    './directives',
    './widgets/worldclock'
], function(angular) {
    'use strict';

    angular.module('superdesk.dashboard', [
        'ngRoute',
        'superdesk.dashboard.directives',
        'superdesk.dashboard.widgets.worldclock'
    ])
    .config(function($routeProvider) {
        $routeProvider.
            when('/', {
                controller: require('superdesk/dashboard/controllers/main'),
                templateUrl: 'scripts/superdesk/dashboard/views/main.html',
                menu: {
                    label: 'Dashboard',
                    priority: 0
                }
            });
    });
});
