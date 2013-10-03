define([
    'angular',
    'angular-route',
    './controllers/main',
    './controllers/worldclock',
    './resources',
    './directives'
], function(angular) {
    'use strict';

    angular.module('superdesk.dashboard', [
        'ngRoute',
        'superdesk.dashboard.resources',
        'superdesk.dashboard.directives',
        'superdesk.dashboard.controllers'
        ]).
        config(function($routeProvider) {

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
