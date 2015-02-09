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
        'superdesk.users',
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
                    privileges: {desks: 1}
                })

                .activity('/settings/desks', {
                    label: gettext('Desks'),
                    controller: require('./controllers/settings'),
                    templateUrl: require.toUrl('./views/settings.html'),
                    category: superdesk.MENU_SETTINGS,
                    priority: -800,
                    privileges: {desks: 1}
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
        .factory('desks', ['$q', 'api', 'preferencesService', 'userList', 'notify',
            function($q, api, preferencesService, userList, notify) {

            var desksService = {
                desks: null,
                users: null,
                stages: null,
                deskLookup: {},
                userLookup: {},
                deskMembers: {},
                deskStages: {},
                loading: null,
                activeDeskId: null,
                activeStageId: null,
                fetchDesks: function() {
                    var self = this;

                    return api.desks.query({max_results: 500})
                    .then(function(result) {
                        self.desks = result;
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
                        _.each(result._items, function(user) {
                            self.userLookup[user._id] = user;
                        });
                    });
                },
                fetchStages: function() {
                    var self = this;

                    return api('stages').query({max_results: 500})
                    .then(function(result) {
                        self.stages = result;
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
                generateDeskStages: function() {
                    var self = this;

                    this.deskStages = _.groupBy(self.stages._items, 'desk');

                    return $q.when();
                },
                fetchUserDesks: function(user) {
                    return api.users.getByUrl(user._links.self.href + '/desks');
                },
                fetchCurrentDeskId: function() {
                    var self = this;
                    return preferencesService.get('desk:items').then(function(result) {
                        if (result && result.length > 0) {
                            self.activeDeskId = result[0];
                        }
                    });
                },
                fetchCurrentStageId: function() {
                    var self = this;
                    return preferencesService.get('stage:items').then(function(result) {
                        if (result && result.length > 0) {
                            self.activeStageId = result[0];
                        }
                    });
                },
                getCurrentDeskId: function() {
                    return this.activeDeskId;
                },
                setCurrentDeskId: function(deskId) {
                    this.activeDeskId = deskId;
                    preferencesService.update({'desk:items': [deskId]}, 'desk:items').then(function() {
                            //nothing to do
                        }, function(response) {
                            notify.error(gettext('Session preference could not be saved...'));
                    });
                },
                getCurrentStageId: function() {
                    return this.activeStageId;
                },
                setCurrentStageId: function(stageId) {
                    this.activeStageId = stageId;
                    preferencesService.update({'stage:items': [stageId]}, 'stage:items').then(function() {
                        //nothing to do
                        }, function(response) {
                            notify.error(gettext('Session preference could not be saved...'));
                    });
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
                initialize: function() {

                    if (!this.loading) {
                        this.fetchCurrentDeskId();
                        this.fetchCurrentStageId();

                        this.loading = this.fetchDesks()
                            .then(angular.bind(this, this.fetchUsers))
                            .then(angular.bind(this, this.generateDeskMembers))
                            .then(angular.bind(this, this.fetchStages))
                            .then(angular.bind(this, this.generateDeskStages));
                    }

                    return this.loading;
                }
            };
            return desksService;
        }]);

    return app;
});
