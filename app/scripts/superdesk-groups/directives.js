define([
    'lodash',
    'angular'
], function(_, angular) {
    'use strict';

    var app = angular.module('superdesk.groups.directives', []);
    app
    .directive('sdUserGroups', ['$rootScope', 'groups', function($rootScope, groups) {
        return {
            scope: {
                selectedGroup: '=group',
                groupLabel: '@'
            },
            templateUrl: 'scripts/superdesk-groups/views/user-groups.html',
            link: function(scope, elem, attrs) {
                groups.fetchUserGroups($rootScope.currentUser).then(function(userGroups) {
                    scope.groups = userGroups._items;
                    scope.selectedGroup = _.find(scope.groups, {_id: groups.getCurrentGroupId()});
                });
                scope.select = function(group) {
                    scope.selectedGroup = group;
                    groups.setCurrentGroup(group);
                };
            }
        };
    }])
    .directive('sdFocusInput', [function() {
        return {
            link: function(scope, elem, attrs) {
                elem.click(function() {
                    _.defer(function() {
                        elem.parent().find('input').focus();
                    });
                });
            }
        };
    }])
    .directive('sdGroupeditBasic', ['gettext', 'api', 'WizardHandler', function(gettext, api, WizardHandler) {
        return {

            link: function(scope, elem, attrs) {

                var _group = null;

                scope.$watch('step.current', function(step) {
                    if (step === 'general') {
                        scope.edit(scope.group.edit);
                        scope.message = null;
                    }
                });

                scope.edit = function(group) {
                    scope.group.edit = _.create(group);
                    _group = group || {};
                };

                scope.save = function(group) {
                    scope.message = gettext('Saving...');
                    var _new = group._id ? false : true;
                    api.groups.save(_group, group).then(function() {
                        if (_new) {
                            scope.edit(_group);
                            scope.groups._items.unshift(_group);
                        }
                        WizardHandler.wizard().next();
                    }, function(response) {
                        scope.message = gettext('There was a problem, group not created/updated.');
                    });
                };
            }
        };
    }])
    .directive('sdGroupeditPeople', ['gettext', 'api', 'WizardHandler', 'groups',
        function(gettext, api, WizardHandler, groups) {
        return {
            link: function(scope, elem, attrs) {

                scope.$watch('step.current', function(step, previous) {
                    if (step === 'people') {
                        scope.search = null;
                        scope.groupMembers = [];
                        scope.users = [];
                        scope.membersToSelect = [];
                        scope.message = null;

                        if (scope.group.edit && scope.group.edit._id) {
                            groups.initialize().then(function() {
                                scope.groupMembers = groups.groupMembers[scope.group.edit._id] || [];
                                scope.users = groups.users._items;
                                generateSearchList();
                            });
                        } else {
                            WizardHandler.wizard().goTo(previous);
                        }
                    }
                });

                function generateSearchList() {
                    scope.membersToSelect = _.difference(scope.users, scope.groupMembers);
                }

                scope.add = function(user) {
                    scope.groupMembers.push(user);
                    generateSearchList();
                    scope.search = null;
                };

                scope.remove = function(user) {
                    _.remove(scope.groupMembers, user);
                    generateSearchList();
                };

                scope.previous = function() {
                    WizardHandler.wizard().previous();
                };

                scope.save = function() {
                    var members = _.map(scope.groupMembers, function(obj) {
                        return {user: obj._id};
                    });

                    api.groups.save(scope.group.edit, {members: members}).then(function(result) {
                        _.extend(scope.group.edit, result);
                        groups.groupMembers[scope.group.edit._id] = scope.groupMembers;
                        WizardHandler.wizard().finish();
                    }, function(response) {
                        scope.message = gettext('There was a problem, members not saved.');
                    });
                };
            }
        };
    }]);
});
