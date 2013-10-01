define([
    'angular',
    'angular-route',
    'bootstrap/dropdown',
    'superdesk/storage',
    './controllers/list',
    './resources'
], function(angular) {
    'use strict';

    angular.module('superdesk.users', ['ngRoute', 'superdesk.users.resources', 'superdesk.storage']).
        config(function($routeProvider) {

            $routeProvider.
                when('/users/', {
                    controller: require('superdesk/users/controllers/list'),
                    templateUrl: 'scripts/superdesk/users/views/list.html',
                    resolve: {
                        users: ['UserListLoader', function(UserListLoader) {
                            return UserListLoader();
                        }]
                    },
                    menu: {
                        label: 'Users',
                        priority: -1
                    }
                });
        }).
        run(function($rootScope) {
            
        });
});
