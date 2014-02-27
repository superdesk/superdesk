define([
    'angular',
    'require',
    './providers',
    './services/profile',
    './controllers/list',
    './controllers/detail',
    './controllers/profile',
    './controllers/edit',
    './controllers/settings',
    './directives'
], function(angular, require) {
    'use strict';

    var app = angular.module('superdesk.users', [
        'superdesk.users.providers',
        'superdesk.users.services',
        'superdesk.users.directives'
    ]);

    app
        .controller('UserDetailCtrl', require('./controllers/detail'))
        .value('defaultListParams', {
            search: '',
            searchField: 'username',
            sort: ['display_name', 'asc'],
            page: 1,
            perPage: 25
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
                locationParams: ['locationParams', 'defaultListParams', '$route',
                    function(locationParams, defaultListParams, $route) {
                        defaultListParams.id = $route.current.params.id;
                        locationParams.reset(defaultListParams);
                        return locationParams;
                    }]
            };

            superdesk
                .activity('/users/', {
                    label: gettext('Users'),
                    priority: 100,
                    controller: require('./controllers/list'),
                    templateUrl: 'scripts/superdesk-users/views/list.html',
                    resolve: usersResolve,
                    category: superdesk.MENU_MAIN,
                    reloadOnSearch: false,
                    filters: [
                        {
                            action: superdesk.ACTION_PREVIEW,
                            type: 'user'
                        }
                    ]
                })
                .activity('/users/:id', {
                    label: gettext('Users profile'),
                    priority: 100,
                    controller: require('./controllers/edit'),
                    templateUrl: 'scripts/superdesk-users/views/edit.html',
                    resolve: {
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
                        roles: ['rolesLoader', function(rolesLoader) {
                            return rolesLoader;
                        }]
                    }
                })
                .activity('/profile/', {
                    label: gettext('My Profile'),
                    controller: require('./controllers/profile'),
                    templateUrl: 'scripts/superdesk-users/views/profile.html',
                    resolve: {
                        user: ['authService', 'em', function(authService, em) {
                            return em.find('users', authService.getIdentity());
                        }]
                    }
                })
                .activity('/settings/user-roles', {
                    label: gettext('User Roles'),
                    templateUrl: 'scripts/superdesk-users/views/settings.html',
                    controller: require('./controllers/settings'),
                    category: superdesk.MENU_SETTINGS,
                    priority: -500
                })
                .activity('delete/user', {
                    label: gettext('Delete user'),
                    icon: 'trash',
                    confirm: gettext('Please confirm you want to delete a user.'),
                    controller: ['em', 'data', 'locationParams', function(em, data, locationParams) {
                        em.remove(data).then(function() {
                            locationParams.reload();
                        });
                    }],
                    filters: [
                        {
                            action: superdesk.ACTION_EDIT,
                            type: 'user'
                        }
                    ]
                });
        }]);
});
