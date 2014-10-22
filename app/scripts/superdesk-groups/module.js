define([
    'angular',
    'lodash',
    './directives'
], function(angular, _) {
    'use strict';

    var app = angular.module('superdesk.groups', [
        'superdesk.users',
        'superdesk.groups.directives'
    ]);

    app
        .config(['superdeskProvider', function(superdesk) {
            superdesk
            .activity('/settings/groups', {
                    label: gettext('Groups'),
                    controller: GroupsSettingsController,
                    templateUrl: 'scripts/superdesk-groups/views/settings.html',
                    category: superdesk.MENU_SETTINGS,
                    priority: -800,
                    beta: true
                });
        }])
        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('groups', {
                type: 'http',
                backend: {
                    rel: 'groups'
                }
            });
        }])
        .factory('groups', ['$q', 'api', 'storage', 'userList', function($q, api, storage, userList) {
            var groupsService = {
                groups: null,
                users: null,
                groupLookup: {},
                userLookup: {},
                groupMembers: {},
                loading: null,
                fetchGroups: function() {
                    var self = this;

                    return api.groups.query({max_results: 500})
                    .then(function(result) {
                        self.groups = result;
                        _.each(result._items, function(group) {
                            self.groupLookup[group._id] = group;
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
                generateGroupMembers: function() {
                    var self = this;

                    _.each(this.groups._items, function(group) {
                        self.groupMembers[group._id] = [];
                        _.each(group.members, function(member, index) {
                            var user = _.find(self.users._items, {_id: member.user});
                            if (user) {
                                self.groupMembers[group._id].push(user);
                            }
                        });
                    });

                    return $q.when();
                },
                fetchUserGroups: function(user) {
                    return api.users.getByUrl(user._links.self.href + '/groups');
                },
                getCurrentGroupId: function() {
                    return storage.getItem('groups:currentGroupId') || null;
                },
                setCurrentGroupId: function(groupId) {
                    storage.setItem('groups:currentGroupId', groupId);
                },
                fetchCurrentGroup: function() {
                    return api.groups.getById(this.getCurrentGroupId());
                },
                setCurrentGroup: function(group) {
                    this.setCurrentGroupId(group ? group._id : null);
                },
                getCurrentGroup: function(group) {
                    return this.groupLookup[this.getCurrentGroupId()];
                },
                initialize: function() {
                    if (!this.loading) {
                        this.loading = this.fetchGroups()
                            .then(angular.bind(this, this.fetchUsers))
                            .then(angular.bind(this, this.generateGroupMembers));
                    }

                    return this.loading;
                }
            };
            return groupsService;
        }]);

        GroupListController.$inject = ['$scope', 'api'];
        function GroupListController($scope, api) {
            api.groups.query()
            .then(function(groups) {
                $scope.groups = groups;
            });
        }

        GroupsSettingsController.$inject = ['$scope', 'gettext', 'notify', 'api', 'groups', 'WizardHandler'];
        function GroupsSettingsController($scope, gettext, notify, api, groups, WizardHandler) {

            $scope.modalActive = false;
            $scope.step = {
                current: null
            };
            $scope.group = {
                edit: null
            };
            $scope.groups = {};

            groups.initialize()
            .then(function() {
                $scope.groups = groups.groups;
            });

            $scope.openGroup = function(step, group) {
                $scope.group.edit = group;
                $scope.modalActive = true;
                WizardHandler.wizard().goTo(step);
            };

            $scope.cancel = function() {
                $scope.modalActive = false;
                $scope.step.current = null;
                $scope.group.edit = null;
            };

			$scope.remove = function(group) {
                api.groups.remove(group).then(function() {
                    _.remove($scope.groups._items, group);
                    notify.success(gettext('Group deleted.'), 3000);
                });
            };

		}

    return app;
});
