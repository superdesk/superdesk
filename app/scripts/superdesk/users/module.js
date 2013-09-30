define([
    'angular',
    'angular-route',
    'bootstrap/dropdown',
    './controllers/list',
    './resources'
], function(angular) {
    'use strict';

    angular.module('superdesk.users', ['ngRoute', 'superdesk.users.resources']).
        config(function($routeProvider) {

            function getUserLoader(defaultParams) {
                return function($route, UserListLoader) {
                    var params = angular.extend({
                        skip: 0,
                        limit: 25
                    }, defaultParams, $route.current.params);
                    return UserListLoader(params);
                };
            }

            $routeProvider.
                when('/users/', {
                    controller: require('superdesk/users/controllers/list'),
                    templateUrl: 'scripts/superdesk/users/views/list.html',
                    resolve: {
                        users: ['UserListLoader', function(UserListLoader) {
                            return UserListLoader({itemClass: 'icls:composite'});
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
