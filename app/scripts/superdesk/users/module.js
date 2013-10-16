define([
    'angular',
    'superdesk/settings',
    'superdesk/state',
    'superdesk/server',
    'superdesk/services/translate',
    './controllers/list',
    './services'
], function(angular) {
    'use strict';

    angular.module('superdesk.users', ['ngRoute', 'superdesk.settings', 'superdesk.state', 'superdesk.server', 'superdesk.users.services']).
        value('defaultListParams', {
            search: '',
            sortField: 'display_name',
            sortDirection: 'asc',
            page: 1,
            perPage: 20
        }).
        value('defaultListSettings', {
            fields: {
                avatar: true,
                display_name: true,
                username: false,
                email: false,
                created: true
            }
        }).
        config(function($routeProvider) {
            $routeProvider.
                when('/users/', {
                    controller: require('superdesk/users/controllers/list'),
                    templateUrl: 'scripts/superdesk/users/views/list.html',
                    resolve: {
                        users: ['server', '$route', 'defaultListParams', 'converter',
                        function(server, $route, defaultListParams, converter) {
                            return server.readList(
                                'users',
                                converter.convert($route.current.params)
                            );
                        }],
                        settings: ['settings', 'defaultListSettings',
                        function(settings, defaultListSettings) {
                            return settings('users:list', defaultListSettings);
                        }],
                        state: ['state', 'defaultListParams', '$route',
                        function(state, defaultListParams, $route) {
                            return state(defaultListParams, $route.current.params);
                        }]
                    },
                    menu: {
                        label: gettext('Users'),
                        priority: -1
                    }
                });
        });
});
