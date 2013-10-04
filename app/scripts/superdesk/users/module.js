define([
    'angular',
    'angular-route',
    'bootstrap/dropdown',
    'superdesk/storage',
    'superdesk/server',
    './controllers/list',
    './services'
], function(angular) {
    'use strict';

    angular.module('superdesk.users', ['ngRoute', 'superdesk.storage', 'superdesk.server', 'superdesk.users.services']).
        value('listDefaults', {
            search: '',
            sortField: 'display_name',
            sortDirection: 'asc',
            page: 1,
            perPage: 20
        }).
        config(function($routeProvider) {
            $routeProvider.
                when('/users/', {
                    controller: require('superdesk/users/controllers/list'),
                    templateUrl: 'scripts/superdesk/users/views/list.html',
                    resolve: {
                        users: ['server', '$route', 'listDefaults', 'converter', function(server, $route, listDefaults, converter) {
                            return server.readList(
                                'users',
                                converter.run(angular.extend({}, listDefaults, $route.current.params))
                            );
                        }]
                    },
                    menu: {
                        label: 'Users',
                        priority: -1
                    }
                });
        });
});
