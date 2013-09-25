define([
    'angular',
    'angular-route',
    'bootstrap/dropdown',
    './controllers/main',
    './controllers/ref',
], function(angular) {
    'use strict';

    angular.module('superdesk.dashboard', ['ngRoute']).
        config(function($routeProvider) {

            $routeProvider.
                when('/', {
                    controller: require('superdesk/dashboard/controllers/main'),
                    templateUrl: 'scripts/superdesk/dashboard/views/main.html',
                    menu: {
                        parent: 'dashboard',
                        label: 'xx',
                        priority: -1
                    }
                });
        }).
        run(function($rootScope) {

        }).
        controller('RefController', require('superdesk/dashboard/controllers/ref'));
});
