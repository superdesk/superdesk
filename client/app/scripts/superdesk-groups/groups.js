(function() {
    'use strict';

    var app = angular.module('superdesk.groups', [
        'superdesk.users'
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
                    beta: true,
                    privileges: {groups: 1}
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
        }])
        .directive('sdGroupeditBasic', GroupeditBasicDirective)
        .directive('sdGroupeditPeople', GroupeditPeopleDirective)
        .directive('sdGroupsConfig', function() {
            return {
                controller: GroupsConfigController
            };
        })
        .directive('sdGroupsConfigModal', function() {
            return {
                require: '^sdGroupsConfig',
                templateUrl: 'scripts/superdesk-groups/views/groups-config-modal.html',
                link: function(scope, elem, attrs, ctrl) {

                }
            };
        });

    GroupsSettingsController.$inject = ['$scope', 'groups'];
    function GroupsSettingsController($scope, groups) {
        groups.initialize().then(function() {
            $scope.groups = groups.groups;
        });
    }

    GroupsConfigController.$inject = ['$scope', 'gettext', 'notify', 'api', 'groups', 'WizardHandler', 'modal'];
    function GroupsConfigController ($scope, gettext, notify, api, groups, WizardHandler, modal) {

        $scope.modalActive = false;
        $scope.step = {
            current: null
        };
        $scope.group = {
            edit: null
        };

        $scope.openGroup = function(step, group) {
            $scope.modalActive = true;
            $scope.step.current = step;
            $scope.group.edit = group;
        };

        $scope.cancel = function() {
            $scope.modalActive = false;
            $scope.step.current = null;
            $scope.group.edit = null;
        };

        $scope.remove = function(group) {
            modal.confirm(gettext('Are you sure you want to delete group?')).then(
                function removeGroup() {
                    api.groups.remove(group).then(function() {
                        _.remove($scope.groups._items, group);
                        notify.success(gettext('Group deleted.'), 3000);
                    });
                }
            );
        };
    }

    GroupeditBasicDirective.$inject = ['gettext', 'api', 'WizardHandler'];
    function GroupeditBasicDirective(gettext, api, WizardHandler) {
        return {
            link: function(scope, elem, attrs) {

                var limits = {
                    group: 40
                };

                scope.limits = limits;

                scope.$watch('step.current', function(step) {
                    if (step === 'general') {
                        scope.edit(scope.group.edit);
                        scope.message = null;
                    }
                });

                scope.edit = function(group) {
                    scope.group.edit = _.create(group);
                };

                scope.save = function(group) {
                    scope.message = gettext('Saving...');
                    var _new = group._id ? false : true;
                    api.groups.save(scope.group.edit, group).then(function() {
                        if (_new) {
                            scope.edit(scope.group.edit);
                            scope.groups._items.unshift(scope.group.edit);
                        } else {
                            var orig = _.find(scope.groups._items, {_id: scope.group.edit._id});
                            _.extend(orig, scope.group.edit);
                        }

                        WizardHandler.wizard('usergroups').next();
                    }, errorMessage);
                };

                function errorMessage(response) {
                    if (response.data && response.data._issues && response.data._issues.name && response.data._issues.name.unique) {
                        scope._errorUniqueness = true;
                    } else {
                        scope._error = true;
                    }
                    scope.message = null;
                }
                function clearErrorMessages() {
                    if (scope._errorUniqueness || scope._error || scope._errorLimits) {
                        scope._errorUniqueness = null;
                        scope._error = null;
                        scope._errorLimits = null;
                    }
                }
                scope.handleEdit = function($event) {
                    clearErrorMessages();
                    if (scope.group.edit.name != null) {
                        scope._errorLimits = scope.group.edit.name.length > scope.limits.group ? true : null;
                    }
                };
            }
        };
    }

    GroupeditPeopleDirective.$inject = ['gettext', 'api', 'WizardHandler', 'groups'];
    function GroupeditPeopleDirective(gettext, api, WizardHandler, groups) {
        return {
            link: function(scope, elem, attrs) {

                scope.$watch('step.current', function(step, previous) {
                    if (step === 'people') {
                        scope.search = null;
                        scope.groupMembers = [];
                        scope.users = [];
                        scope.message = null;

                        if (scope.group.edit && scope.group.edit._id) {
                            groups.initialize().then(function() {
                                scope.groupMembers = groups.groupMembers[scope.group.edit._id] || [];
                                scope.users = groups.users._items;
                            });
                        } else {
                            WizardHandler.wizard('usergroups').goTo(previous);
                        }
                    }
                });

                scope.add = function(user) {
                    scope.groupMembers.push(user);
                };

                scope.remove = function(user) {
                    _.remove(scope.groupMembers, user);
                };

                scope.previous = function() {
                    WizardHandler.wizard('usergroups').previous();
                };

                scope.save = function() {
                    var members = _.map(scope.groupMembers, function(obj) {
                        return {user: obj._id};
                    });

                    api.groups.save(scope.group.edit, {members: members}).then(function(result) {
                        _.extend(scope.group.edit, result);
                        groups.groupMembers[scope.group.edit._id] = scope.groupMembers;
                        var orig = _.find(groups.groups._items, {_id: scope.group.edit._id});
                        _.extend(orig, scope.group.edit);
                        WizardHandler.wizard('usergroups').finish();
                    }, function(response) {
                        scope.message = gettext('There was a problem, members not saved.');
                    });
                };
            }
        };
    }

    return app;
})();
