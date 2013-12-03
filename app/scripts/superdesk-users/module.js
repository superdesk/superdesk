define([
    'angular',
    './providers',
    './controllers/list',
    './controllers/detail',
    './controllers/profile',
    './controllers/settings',
    './directives/sdUserPicture',
    './directives/sdUserActivity',
    './directives/sdRolesTreeview',
    './directives/sdInfoItem',
    './directives/sdUserEdit',
    './directives/sdUserDetailsPane',
    './services/profile',
], function(angular) {
    'use strict';

    angular.module('superdesk.users', ['superdesk.entity', 'superdesk.userSettings', 'superdesk.auth', 'superdesk.users.providers'])
        .service('profileService', require('superdesk-users/services/profile'))
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
        .config(function(permissionsProvider) {
            permissionsProvider.permission('users-manage', {
                label: 'Manage users',
                permissions: {users: {write: true}}
            });
            permissionsProvider.permission('users-read', {
                label: 'Read users',
                permissions: {users: {read: true}}
            });
            permissionsProvider.permission('user-roles-manage', {
                label: 'Manage user roles',
                permissions: {'user-roles': {write: true}}
            });
            permissionsProvider.permission('user-roles-read', {
                label: 'Read user roles',
                permissions: {'user-roles': {read: true}}
            });
        })
        .config(function(activityProvider) {
            activityProvider
                .activity('users-list', {
                    href: '/users/:id?',
                    menuHref: '/users/',
                    label: gettext('Users'),
                    priority: -1,
                    controller: require('superdesk-users/controllers/list'),
                    templateUrl: 'scripts/superdesk-users/views/list.html',
                    resolve: {
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
                    }
                })
                .activity('users-profile', {
                    href: '/profile/',
                    label: gettext('My Profile'),
                    menu: false,
                    controller: require('superdesk-users/controllers/profile'),
                    templateUrl: 'scripts/superdesk-users/views/profile.html',
                    resolve: {
                        user: ['authService', 'em', function(authService, em) {
                            return em.find('users', authService.getIdentity());
                        }]
                    }
                });
        })
        .config(function(settingsProvider) {
            settingsProvider.register('user-roles', {
                label: gettext('User Roles'),
                templateUrl: 'scripts/superdesk-users/views/settings.html'
            });
        });
});
