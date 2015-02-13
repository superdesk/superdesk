define([
    'require',
    './directives'
], function(require) {
    'use strict';

    DeskListController.$inject = ['$scope', 'api'];
    function DeskListController($scope, api) {
        api.desks.query()
            .then(function(desks) {
                $scope.desks = desks;
            });
    }

    DeskSettingsController.$inject = ['$scope', 'gettext', 'notify', 'desks', 'WizardHandler'];
    function DeskSettingsController ($scope, gettext, notify, desks, WizardHandler) {
        $scope.modalActive = false;
        $scope.step = {
            current: null
        };
        $scope.desk = {
            edit: null
        };
        $scope.desks = {};

        desks.initialize()
        .then(function() {
            $scope.desks = desks.desks;
        });

        $scope.openDesk = function(step, desk) {
            $scope.desk.edit = desk;
            $scope.modalActive = true;
            $scope.step.current = step;
        };

        $scope.cancel = function() {
            $scope.modalActive = false;
            $scope.step.current = null;
            $scope.desk.edit = null;
        };

        $scope.remove = function(desk) {
            desks.remove(desk).then(function() {
                _.remove($scope.desks._items, desk);
                notify.success(gettext('Desk deleted.'), 3000);
            });
        };

        function getExpiryHours(inputMin) {
            return Math.floor(inputMin / 60);
        }
        function getExpiryMinutes(inputMin) {
            return Math.floor(inputMin % 60);
        }
        $scope.getTotalExpiryMinutes = function(contentExpiry) {
            return (contentExpiry.Hours * 60) + contentExpiry.Minutes;
        };

        $scope.setContentExpiryHoursMins = function(container) {
            var objContentExpiry = {
                Hours: 0,
                Minutes: 0
            };
            if (container.content_expiry != null) {
                objContentExpiry.Hours = getExpiryHours(container.content_expiry);
                objContentExpiry.Minutes = getExpiryMinutes(container.content_expiry);
            }
            return objContentExpiry;
        };

        $scope.setSpikeExpiryHoursMins = function(container) {
            var objSpikeExpiry = {
                Hours: 0,
                Minutes: 0
            };

            if (container.spike_expiry != null) {
                objSpikeExpiry.Hours = getExpiryHours(container.spike_expiry);
                objSpikeExpiry.Minutes = getExpiryMinutes(container.spike_expiry);
            }
            return objSpikeExpiry;
        };
    }

    var app = angular.module('superdesk.desks', [
        'superdesk.users',
        'superdesk.desks.directives'
    ]);

    app
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/desks/', {
                    label: gettext('Desks'),
                    templateUrl: require.toUrl('./views/main.html'),
                    controller: DeskListController,
                    category: superdesk.MENU_MAIN,
                    privileges: {desks: 1}
                })

                .activity('/settings/desks', {
                    label: gettext('Desks'),
                    controller: DeskSettingsController,
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
        .factory('desks', ['$q', 'api', 'preferencesService', 'userList', 'notify', 'session',
            function($q, api, preferencesService, userList, notify, session) {

                var userDesks, userDesksPromise;

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
                    return api.get(user._links.self.href + '/desks')
                        .then(function(response) {
                            return response._items;
                        });
                },

                fetchCurrentUserDesks: function() {
                    if (userDesks) {
                        return $q.when(userDesks);
                    }

                    if (!userDesksPromise) {
                        userDesksPromise = this.fetchCurrentDeskId() // make sure there will be current desk
                            .then(angular.bind(session, session.getIdentity))
                            .then(angular.bind(this, this.fetchUserDesks))
                            .then(function(desks) {
                                userDesks = desks;
                                return desks;
                            });
                    }

                    return userDesksPromise;
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
                },
                save: function(dest, diff) {
                    return api.save('desks', dest, diff)
                        .then(reset);
                },
                remove: function(desk) {
                    return api.remove(desk)
                        .then(reset);
                }
            };

            function reset(res) {
                userDesks = null;
                userDesksPromise = null;
                desksService.loading = null;
                return res;
            }

            return desksService;
        }]);

    return app;
});
