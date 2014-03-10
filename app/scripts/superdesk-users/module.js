define([
    'angular',
    'require',
    './providers',
    './services/profile',
    './controllers/list',
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
                        user: ['resource', '$route', function(resource, $route) {
                            return resource.users.getById($route.current.params.id);
                        }]
                    }
                })
                .activity('/profile/', {
                    label: gettext('My Profile'),
                    controller: require('./controllers/profile'),
                    templateUrl: 'scripts/superdesk-users/views/profile.html',
                    resolve: {
                        user: ['session', 'resource', function(session, resource) {
                            return resource.users.getByUrl(session.identity.href);
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
                    controller: ['resource', 'data', function(resource, data) {
                        return resource.users.remove(data.item).then(function() {
                            data.list.splice(data.index, 1);
                        });
                    }],
                    filters: [
                        {
                            action: superdesk.ACTION_EDIT,
                            type: 'user'
                        }
                    ]
                });
        }])
        .config(['resourceProvider', function(resourceProvider) {
            resourceProvider.resource('users', {rel: 'HR/User', headers: {'X-Filter': 'User.*'}});
        }]);
});
