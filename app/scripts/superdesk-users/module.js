define([
    'angular',
    'require',
    './providers',
    './services/profile',
    './controllers/list',
    './controllers/detail',
    './controllers/profile',
    './controllers/settings',
    './directives/sdUserPicture',
    './directives/sdUserActivity',
    './directives/sdRolesTreeview',
    './directives/sdInfoItem',
    './directives/sdUserEdit',
    './directives/sdUserDetailsPane'
], function(angular, require) {
    'use strict';

    var app = angular.module('superdesk.users', [
        'superdesk.users.providers',
        'superdesk.users.services'
    ]);

    app
        .controller('RolesSettingsCtrl', require('superdesk-users/controllers/settings'))
        .controller('UserDetailCtrl', require('superdesk-users/controllers/detail'))
        .directive('sdUserPicture', require('superdesk-users/directives/sdUserPicture'))
        .directive('sdUserActivity', require('superdesk-users/directives/sdUserActivity'))
        .directive('sdInfoItem', require('superdesk-users/directives/sdInfoItem'))
        .directive('sdUserEdit', require('superdesk-users/directives/sdUserEdit'))
        .directive('sdUserDetailsPane', require('superdesk-users/directives/sdUserDetailsPane'))
        .directive('sdRolesTreeview', require('superdesk-users/directives/sdRolesTreeview'))
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
                user_role: true,
                username: false,
                email: false,
                created: true
            }
        })
        .config(['permissionsProvider', function(permissionsProvider) {
            permissionsProvider.permission('users-manage', {
                label: gettext('Manage users'),
                permissions: {users: {write: true}}
            });
            permissionsProvider.permission('users-read', {
                label: gettext('Read users'),
                permissions: {users: {read: true}}
            });
            permissionsProvider.permission('user-roles-manage', {
                label: gettext('Manage user roles'),
                permissions: {'user_roles': {write: true}}
            });
            permissionsProvider.permission('user-roles-read', {
                label: gettext('Read user roles'),
                permissions: {'user_roles': {read: true}}
            });
        }])
        .config(['superdeskProvider', function(superdesk) {

            var usersResolve = {
                users: ['locationParams', 'em', 'defaultListParams',
                    function(locationParams, em, defaultListParams) {
                        var criteria = locationParams.reset(defaultListParams);
                        return em.getRepository('users').matching(criteria);
                    }],
                user: ['em', '$route',
                    function(em, $route) {
                        if ($route.current.params.id === 'new') {
                            return {};
                        } else if (_.isString($route.current.params.id)) {
                            return em.find('users', $route.current.params.id);
                        } else {
                            return undefined;
                        }
                    }],
                userSettings: ['userSettings', 'defaultListSettings',
                    function(userSettings, defaultListSettings) {
                        return userSettings('users:list', defaultListSettings);
                    }],
                locationParams: ['locationParams', 'defaultListParams', '$route',
                    function(locationParams, defaultListParams, $route) {
                        defaultListParams.id = $route.current.params.id;
                        locationParams.reset(defaultListParams);
                        return locationParams;
                    }],
                roles: ['rolesLoader', function(rolesLoader) {
                    return rolesLoader;
                }]
            };

            superdesk
                .activity('users-list', {
                    when: '/users/:id?',
                    href: '/users/',
                    label: gettext('Users'),
                    priority: 100,
                    controller: require('./controllers/list'),
                    templateUrl: 'scripts/superdesk-users/views/list.html',
                    resolve: usersResolve,
                    category: superdesk.MENU_MAIN
                })
                .activity('users-profile', {
                    href: '/profile/',
                    label: gettext('My Profile'),
                    controller: require('./controllers/profile'),
                    templateUrl: 'scripts/superdesk-users/views/profile.html',
                    resolve: {
                        user: ['authService', 'em', function(authService, em) {
                            return em.find('users', authService.getIdentity());
                        }]
                    }
                });
        }])
        .config(['settingsProvider', function(settingsProvider) {
            settingsProvider.register('user-roles', {
                label: gettext('User Roles'),
                templateUrl: 'scripts/superdesk-users/views/settings.html'
            });
        }]);
});
