define([
    'angular',
    'angular-route',
    'bootstrap/dropdown',
    './controllers/main'
], function(angular) {
    'use strict';

    angular.module('superdesk.dashboard', ['ngRoute']).
        config(function($routeProvider) {

            $routeProvider.
                when('/', {
                    controller: require('superdesk/dashboard/controllers/main'),
                    templateUrl: 'scripts/superdesk/dashboard/views/main.html'
                });
        });
});
