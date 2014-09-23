define([
    'angular',
    'require',
    './providers',
    './users-service',
    './userlist-service',
    './services/profile',
    './controllers/list',
    './controllers/edit',
    './controllers/settings',
    './controllers/changeAvatar',
    './activity-widget/activity',
    './directives'
], function(angular, require) {
    'use strict';

    /**
     * Delete a user and remove it from list
     */
    UserDeleteCommand.$inject = ['api', 'data', '$q', 'notify', 'gettext'];
    function UserDeleteCommand(api, data, $q, notify, gettext) {
        return api.users.remove(data.item).then(function(response) {
            data.list.splice(data.index, 1);
        }, function(response) {
            notify.error(gettext('I\'m sorry but can\'t delete the user right now.'));
        });
    }

    /**
     * Resolve a user by route id and redirect to /users if such user does not exist
     */
    UserResolver.$inject = ['api', '$route', 'notify', 'gettext', '$location'];
    function UserResolver(api, $route, notify, gettext, $location) {
        return api.users.getById($route.current.params._id)
            .then(null, function(response) {
                if (response.status === 404) {
                    $location.path('/users/');
                    notify.error(gettext('User was not found, sorry.'), 5000);
                }

                return response;
            });
    }

    var app = angular.module('superdesk.users', [
        'superdesk.users.providers',
        'superdesk.users.services',
        'superdesk.users.directives',
        'superdesk.widgets.activity'
    ]);

    app
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

            superdesk
                .activity('/users/', {
                    label: gettext('Users'),
                    priority: 100,
                    controller: require('./controllers/list'),
                    templateUrl: require.toUrl('./views/list.html'),
                    category: superdesk.MENU_MAIN,
                    reloadOnSearch: false,
                    filters: [
                        {
                            action: superdesk.ACTION_PREVIEW,
                            type: 'user'
                        },
                        {action: 'list', type: 'user'}
                    ]
                })
                .activity('/users/:_id', {
                    label: gettext('Users profile'),
                    priority: 100,
                    controller: require('./controllers/edit'),
                    templateUrl: require.toUrl('./views/edit.html'),
                    resolve: {user: UserResolver},
                    filters: [{action: 'detail', type: 'user'}]
                })
                .activity('/profile/', {
                    label: gettext('My Profile'),
                    controller: require('./controllers/edit'),
                    templateUrl: require.toUrl('./views/edit.html'),
                    resolve: {
                        user: ['session', 'api', function(session, api) {
                            console.log(session.identity._links);
                            return api.users.getByUrl(session.identity._links.self.href);
                        }]
                    }
                })

                /*
                .activity('/settings/user-roles', {
                    label: gettext('User Roles'),
                    templateUrl: require.toUrl('./views/settings.html'),
                    controller: require('./controllers/settings'),
                    category: superdesk.MENU_SETTINGS,
                    priority: -500
                })
                */

                .activity('delete/user', {
                    label: gettext('Delete user'),
                    icon: 'trash',
                    confirm: gettext('Please confirm you want to delete a user.'),
                    controller: UserDeleteCommand,
                    filters: [
                        {
                            action: superdesk.ACTION_EDIT,
                            type: 'user'
                        }
                    ]
                })
                .activity('edit.avatar', {
                    label: gettext('Change avatar'),
                    modal: true,
                    cssClass: 'upload-avatar',
                    controller: require('./controllers/changeAvatar'),
                    templateUrl: require.toUrl('./views/change-avatar.html'),
                    filters: [{action: 'edit', type: 'avatar'}]
                });
        }])
        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('users', {
                type: 'http',
                backend: {rel: 'users'},
                service: require('./users-service')
            });
        }])
        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('activity', {
                type: 'http',
                backend: {rel: 'activity'},
                service: require('./services/profile')
            });
        }])
        .factory('userList', require('./userlist-service'));

    return app;
});
