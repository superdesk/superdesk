define([
    'angular',
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

    angular.module('superdesk.users', ['superdesk.entity', 'superdesk.userSettings', 'superdesk.auth'])
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
        .config(function(activityProvider) {
            activityProvider
                .activity('users-create', {
                    permission: {
                        label: 'Create users',
                        users: ['create']
                    }
                })
                .activity('users-read', {
                    permission: {
                        label: 'Read user details',
                        users: ['read']
                    }
                })
                .activity('users-update', {
                    permission: {
                        label: 'Update users',
                        users: ['update']
                    }
                })
                .activity('users-delete', {
                    permission: {
                        label: 'Delete users',
                        users: ['delete']
                    }
                })
                .activity('users-list', {
                    permission: {
                        label: 'List users',
                        users: ['read']
                    },
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
