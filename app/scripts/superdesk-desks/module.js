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
        .factory('desks', ['$q', 'api', 'storage', 'userList', function($q, api, storage, userList) {
            var desksService = {
                desks: null,
                users: null,
                deskLookup: {},
                userLookup: {},
                deskMembers: {},
                fetchDesks: function() {
                    var self = this;

                    return api.desks.query({max_results: 500})
                    .then(function(result) {
                        self.desks = result;
                        self.deskLookup = {};
                        _.each(result._items, function(desk) {
                            self.deskLookup[desk._id] = desk;
                        });
                    });
                },
                fetchUsers: function() {
                    var self = this;

                    return userList.get(null, 1, 500)
                    .then(function(result) {
                        self.users = result;
                        self.userLookup = {};
                        _.each(result._items, function(user) {
                            self.userLookup[user._id] = user;
                        });
                    });
                },
                generateDeskMembers: function() {
                    var self = this;

                    _.each(this.desks._items, function(desk) {
                        self.deskMembers[desk._id] = [];
                        _.each(desk.members, function(member, index) {
                            var user = _.find(self.users._items, {_id: member.user});
                            if (user) {
                                self.deskMembers[desk._id].push(user);
                            }
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
                getCurrentDesk: function(desk) {
                    return this.deskLookup[this.getCurrentDeskId()];
                },
                initialize: function(force) {
                    var self = this;

                    var p = $q.when();
                    if (!this.desks || force) {
                        p = p.then(function() {
                            return self.fetchDesks();
                        });
                    }
                    if (!this.users || force) {
                        p = p.then(function() {
                            return self.fetchUsers();
                        });
                    }
                    if (_.isEmpty(this.deskMembers) || force) {
                        p = p.then(function() {
                            return self.generateDeskMembers();
                        });
                    }
                    return p;
                }
            };
            return desksService;
        }]);

    return app;
});
