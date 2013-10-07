define([
    'angular',
    'angular-route',
    'bootstrap/dropdown',
    'superdesk/settings',
    'superdesk/server',
    './controllers/list',
    './services'
], function(angular) {
    'use strict';

    angular.module('superdesk.users', ['ngRoute', 'superdesk.settings', 'superdesk.server', 'superdesk.users.services']).
        value('defaultListParams', {
            search: '',
            sortField: 'display_name',
            sortDirection: 'asc',
            page: 1,
            perPage: 20
        }).
        value('defaultSettings', {
            fields: {
                avatar: true,
                display_name: true,
                username: false,
                email: false,
                _created: true
            }
        }).
        config(function($routeProvider) {
            $routeProvider.
                when('/users/', {
                    controller: require('superdesk/users/controllers/list'),
                    templateUrl: 'scripts/superdesk/users/views/list.html',
                    resolve: {
                        users: ['server', '$route', 'defaultListParams', 'converter', function(server, $route, defaultListParams, converter) {
                            return server.readList(
                                'users',
                                converter.convert($route.current.params)
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
