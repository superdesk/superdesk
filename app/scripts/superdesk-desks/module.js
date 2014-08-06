define([
    'angular',
    'require',
    'lodash',
    './resources',
    './controllers/main',
    './controllers/settings',
    './directives'
], function(angular, require, _) {
    'use strict';

    var app = angular.module('superdesk.desks', [
        'superdesk.desks.resources',
        'superdesk.desks.directives'
    ]);

    app
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/desks/', {
                    label: gettext('Desks'),
                    templateUrl: require.toUrl('./views/main.html'),
                    controller: require('./controllers/main'),
                    category: superdesk.MENU_MAIN,
                    beta: true
                })

                .activity('/settings/desks', {
                    label: gettext('Desks'),
                    controller: require('./controllers/settings'),
                    templateUrl: require.toUrl('./views/settings.html'),
                    category: superdesk.MENU_SETTINGS,
                    priority: -800,
                    beta: true
                });
        }])
        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('desks', {
                type: 'http',
                backend: {
                    rel: 'desks'
                }
            });
        }])
        .service('desks', ['$q', 'api', 'storage', function($q, api, storage) {
            return {
                desks: null,
                users: null,
                deskMembers: {},
                fetchDesks: function() {
                    var self = this;

                    return api.desks.query()
                    .then(function(result) {
                        self.desks = result;
                    });
                },
                fetchUsers: function() {
                    var self = this;

                    return api.users.query()
                    .then(function(result) {
                        self.users = result;
                    });
                },
                generateDeskMembers: function() {
                    var self = this;

                    _.each(this.desks._items, function(desk) {
                        self.deskMembers[desk._id] = [];
                        _.each(desk.members, function(member, index) {
                            self.deskMembers[desk._id].push(_.find(self.users._items, {_id: member.user}));
                        });
                    });

                    return $q.when();
                },
                fetchUserDesks: function(user) {
                    return api.users.getByUrl(user._links.self.href + '/desks');
                },
                getCurrentDeskId: function() {
                    return storage.getItem('desks:currentDeskId') || null;
                },
                setCurrentDeskId: function(deskId) {
                    storage.setItem('desks:currentDeskId', deskId);
                },
                fetchCurrentDesk: function() {
                    return api.desks.getById(this.getCurrentDeskId());
                },
                setCurrentDesk: function(desk) {
                    this.setCurrentDeskId(desk ? desk._id : null);
                },
                initialize: function() {
                    var self = this;

                    return this.fetchDesks()
                    .then(function() {
                        return self.fetchUsers();
                    })
                    .then(function() {
                        return self.generateDeskMembers();
                    });
                }
            };
        }]);

    return app;
});
