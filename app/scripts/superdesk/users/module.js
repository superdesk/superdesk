define([
    'angular',
    'superdesk/settings',
    'superdesk/server',
    'superdesk/services/translate',
    'superdesk/entity',
    './controllers/list',
    './controllers/detail',
    './services'
], function(angular) {
    'use strict';

    angular.module('superdesk.users', ['superdesk.entity', 'superdesk.settings', 'superdesk.server', 'superdesk.users.services'])
        .value('defaultListParams', {
            search: '',
            searchField: 'username',
            sort: ['display_name', 'asc'],
            page: 1,
            perPage: 25
        })
        .value('defaultListSettings', {
            fields: {
                avatar: true,
                display_name: true,
                username: false,
                email: false,
                created: true
            }
        })
        .controller('UserListController', require('superdesk/users/controllers/list'))
        .controller('UserDetailController', require('superdesk/users/controllers/detail'))
        .config(function($routeProvider) {
            $routeProvider
                .when('/users/:id?', {
                    controller: require('superdesk/users/controllers/list'),
                    templateUrl: 'scripts/superdesk/users/views/list.html',
                    resolve: {
                        users: ['locationParams', 'em', 'defaultListParams',
                        function(locationParams, em, defaultListParams) {
                            var criteria = locationParams.reset(defaultListParams);
                            return em.getRepository('users').matching(criteria);
                        }],
                        user: ['server', '$route',
                        function(server, $route) {
                            if ($route.current.params.id === 'new') {
                                return {}
                            } else if (_.isString($route.current.params.id)) {
                                return server.readById('users', $route.current.params.id);
                            } else {
                                return undefined;
                            }
                        }],
                        settings: ['settings', 'defaultListSettings',
                        function(settings, defaultListSettings) {
                            return settings('users:list', defaultListSettings);
                        }],
                        locationParams: ['locationParams', 'defaultListParams', '$route',
                        function(locationParams, defaultListParams, $route) {
                            defaultListParams.id = $route.current.params.id;
                            locationParams.reset(defaultListParams);
                            return locationParams;
                        }]
                    }
                })
                // temporary fake route, just to have menu fixed
                .when('/users', {
                    menu: {
                        label: gettext('Users'),
                        priority: -1
                    }
                });
        });
});
