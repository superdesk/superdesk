define([
    'angular',
    'superdesk/settings',
    'superdesk/state',
    'superdesk/server',
    'superdesk/services/translate',
    'superdesk/entity',
    './controllers/list',
    './services'
], function(angular) {
    'use strict';

    angular.module('superdesk.users', ['superdesk.entity', 'superdesk.settings', 'superdesk.state', 'superdesk.server', 'superdesk.users.services']).
        value('defaultListParams', {
            search: '',
            sort: ['display_name', 'asc'],
            page: 1,
            perPage: 25
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
                        users: ['locationParams', 'em', 'defaultListParams',
                        function(locationParams, em, defaultListParams) {
                            var criteria = locationParams.reset(defaultListParams);
                            return em.getRepository('users').matching(criteria);
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
