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
        .controller('UserDetailCtrl', require('./controllers/detail'))
        .directive('sdUserPicture', require('./directives/sdUserPicture'))
        .directive('sdUserActivity', require('./directives/sdUserActivity'))
        .directive('sdInfoItem', require('./directives/sdInfoItem'))
        .directive('sdUserEdit', require('./directives/sdUserEdit'))
        .directive('sdUserDetailsPane', require('./directives/sdUserDetailsPane'))
        .directive('sdRolesTreeview', require('./directives/sdRolesTreeview'))
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
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .permission('users-manage', {
                    label: gettext('Manage users'),
                    permissions: {users: {write: true}}
                })
                .permission('users-read', {
                    label: gettext('Read users'),
                    permissions: {users: {read: true}}
                })
                .permission('user-roles-manage', {
                    label: gettext('Manage user roles'),
                    permissions: {'user_roles': {write: true}}
                })
                .permission('user-roles-read', {
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
                    when: '/profile/',
                    label: gettext('My Profile'),
                    controller: require('./controllers/profile'),
                    templateUrl: 'scripts/superdesk-users/views/profile.html',
                    resolve: {
                        user: ['authService', 'em', function(authService, em) {
                            return em.find('users', authService.getIdentity());
                        }]
                    }
                })
                .activity('settings-user-roles', {
                    when: '/settings/user-roles',
                    label: gettext('User Roles'),
                    templateUrl: 'scripts/superdesk-users/views/settings.html',
                    controller: require('./controllers/settings'),
                    category: superdesk.MENU_SETTINGS,
                    priority: -500
                })
                .activity('delete:user', {
                    label: gettext('Delete user'),
                    category: 'user.list',
                    confirm: gettext('Please confirm you want to delete a user.'),
                    controller: ['em', 'data', 'locationParams', function(em, data, locationParams) {
                        em.remove(data).then(function() {
                            locationParams.reload();
                        });
                    }]
                });
        }]);
});
