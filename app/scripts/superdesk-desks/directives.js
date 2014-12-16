define([
    'require',
    'lodash',
    'angular'
], function(require, _, angular) {
    'use strict';

    var app = angular.module('superdesk.desks.directives', []);
    app
    .directive('sdUserDesks', ['$rootScope', 'desks', function($rootScope, desks) {
        return {
            scope: {
                selectedDesk: '=desk',
                deskLabel: '@'
            },
            templateUrl: require.toUrl('./views/user-desks.html'),
            link: function(scope, elem, attrs) {
                scope.tasks = scope.deskLabel === 'tasks' ? true : false;
                desks.fetchUserDesks($rootScope.currentUser).then(function(userDesks) {
                    scope.desks = userDesks._items;
                    scope.selectedDesk = _.find(scope.desks, {_id: desks.getCurrentDeskId()});
                });
                scope.select = function(desk) {
                    scope.selectedDesk = desk;
                    desks.setCurrentDesk(desk);
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
    .directive('sdDeskeditBasic', ['gettext', 'api', 'WizardHandler', function(gettext, api, WizardHandler) {
        return {

            link: function(scope, elem, attrs) {

                scope.$watch('step.current', function(step) {
                    if (step === 'general') {
                    	if (scope.desk.edit && scope.desk.edit._id) {
                    		scope.edit(scope.desk.edit);
                    	}
                        scope.message = null;
                    }
                });

                scope.edit = function(desk) {
                    scope.desk.edit = _.create(desk);
                };

                scope.save = function(desk) {
                    scope.message = gettext('Saving...');
                    var _new = desk._id ? false : true;
                    api.desks.save(scope.desk.edit, desk).then(function() {
                        if (_new) {
                            scope.edit(scope.desk.edit);
                            scope.desks._items.unshift(scope.desk.edit);
                        } else {
                            var origDesk = _.find(scope.desks._items, {_id: scope.desk.edit._id});
                            _.extend(origDesk, scope.desk.edit);
                        }
                        WizardHandler.wizard('desks').next();
                    }, function(response) {
                        scope.message = gettext('There was a problem, desk not created/updated.');
                    });
                };
            }
        };
    }])
    .directive('sdDeskeditStages', ['gettext', 'api', 'WizardHandler',
        function(gettext, api, WizardHandler) {
        return {

            link: function(scope, elem, attrs) {
                scope.origEditName = null;

                scope.$watch('step.current', function(step, previous) {
                    if (step === 'stages') {
                        scope.editStage = null;
                        scope.stages = [];
                        scope.newStage = {
                            show: false,
                            model: null
                        };
                        scope.message = null;

                        if (scope.desk.edit && scope.desk.edit._id) {
                            scope.message = null;
                            api('stages').query({where: {desk: scope.desk.edit._id}})
                            .then(function(result) {
                                scope.stages = result._items;
                            });
                        } else {
                            WizardHandler.wizard('desks').goTo(previous);
                        }
                    }
                });

                scope.previous = function() {
                    WizardHandler.wizard('desks').previous();
                };

                scope.next = function() {
                    WizardHandler.wizard('desks').next();
                };

                scope.saveOnEnter = function($event) {
                    if ($event.keyCode === 13) {
                        scope.message = gettext('Saving...');
                        api('stages').save({}, {name: scope.newStage.model, desk: scope.desk.edit._id})
                        .then(function(item) {
                            scope.stages.push(item);
                            scope.newStage.model = null;
                            scope.newStage.show = false;
                            scope.message = gettext('Stage added successfully.');
                        }, function(response) {
                            scope.message = gettext('There was a problem, stage not added.');
                        });
                        return false;
                    }
                };

                scope.saveEditOnEnter = function($event) {
                    if ($event.keyCode === 13) {
                        scope.message = gettext('Saving...');
                        api('stages').save(scope.editStage)
                        .then(function(item) {
                            scope.editStage = null;
                            scope.message = gettext('Stage saved successfully.');
                        }, function(response) {
                            scope.message = gettext('There was a problem, stage was not saved.');
                        });
                        return false;
                    }
                };

                scope.setEditStage = function(stage) {
                    scope.origEditName = stage.name;
                    scope.editStage = stage;
                    scope.newStage.show = false;
                };

                scope.cancelEdit = function() {
                    if (scope.editStage && scope.editStage.name) {
                        scope.editStage.name = scope.origEditName;
                    }
                    scope.editStage = null;
                };

                scope.remove = function(stage) {
                    api('stages').remove(stage)
                    .then(function(result) {
                        _.remove(scope.stages, stage);
                    }, function(data, status, headers, config) {
                        if (data.data._message) {
                            scope.message = gettext(data.data._message);
                        } else {
                            scope.message = gettext('There was a problem, stage was not deleted.');
                        }
                    });
                };
            }
        };
    }])
    .directive('sdUserSelectList', ['$filter', function($filter) {
        return {
            scope: {
                users: '=',
                onchoose: '&'
            },
            templateUrl: 'scripts/superdesk-desks/views/user-select.html',
            link: function(scope, elem, attrs) {

                var ARROW_UP = 38, ARROW_DOWN = 40, ENTER = 13;

                scope.selected = null;
                scope.search = null;
                scope.filteredUsers = [];

                scope.$watchGroup(['search', 'users'], function() {
                    scope.filteredUsers = $filter('filter')(scope.users, scope.search);
                    scope.selected = null;
                });

                function getSelectedIndex() {
                    if (scope.selected) {
                        return _.findIndex(scope.filteredUsers, scope.selected);
                    } else {
                        return -1;
                    }
                }

                function previous() {
                    var selectedIndex = getSelectedIndex();
                    if (selectedIndex > 0) {
                        scope.select(scope.filteredUsers[_.max([0, selectedIndex - 1])]);
                    }
                }

                function next() {
                    var selectedIndex = getSelectedIndex();
                    scope.select(scope.filteredUsers[_.min([scope.filteredUsers.length - 1, selectedIndex + 1])]);
                }

                elem.bind('keydown keypress', function(event) {
                    scope.$apply(function() {
                        switch (event.which) {
                            case ARROW_UP:
                                event.preventDefault();
                                previous();
                                break;
                            case ARROW_DOWN:
                                event.preventDefault();
                                next();
                                break;
                            case ENTER:
                                event.preventDefault();
                                if (getSelectedIndex() >= 0) {
                                	scope.choose(scope.selected);
                                }
                                break;
                        }
                    });
                });

                scope.choose = function(user) {
                    scope.onchoose({user: user});
                    scope.search = null;
                };

                scope.select = function(user) {
                    scope.selected = user;
                };
            }
        };
    }])
    .directive('sdDeskeditPeople', ['gettext', 'api', 'WizardHandler', 'desks', 'keyboardManager',
        function(gettext, api, WizardHandler, desks, keyboardManager) {
        return {
            link: function(scope, elem, attrs) {

                scope.$watch('step.current', function(step, previous) {
                    if (step === 'people') {
                        scope.search = null;
                        scope.deskMembers = [];
                        scope.users = [];
                        scope.membersToSelect = [];
                        scope.message = null;

                        if (scope.desk.edit && scope.desk.edit._id) {
                        	desks.fetchUsers().then(function(result) {
                        		scope.users = desks.users._items;
                            	scope.deskMembers = desks.deskMembers[scope.desk.edit._id] || [];
                                generateSearchList();
                            });
                        } else {
                            WizardHandler.wizard('desks').goTo(previous);
                        }
                    }
                });

                function generateSearchList() {
                    scope.membersToSelect = _.filter(scope.users, function(obj) { return !_.findWhere(scope.deskMembers, obj); });
                }

                scope.add = function(user) {
                    scope.deskMembers.push(user);
                    generateSearchList();
                };

                scope.remove = function(user) {
                    _.remove(scope.deskMembers, user);
                    generateSearchList();
                };

                scope.previous = function() {
                    WizardHandler.wizard('desks').previous();
                };

                scope.save = function() {
                    var members = _.map(scope.deskMembers, function(obj) {
                        return {user: obj._id};
                    });

                    api.desks.save(scope.desk.edit, {members: members}).then(function(result) {
                        _.extend(scope.desk.edit, result);
                        desks.deskMembers[scope.desk.edit._id] = scope.deskMembers;
                        var origDesk = desks.deskLookup[scope.desk.edit._id];
                        _.extend(origDesk, scope.desk.edit);
                        WizardHandler.wizard('desks').finish();
                    }, function(response) {
                        scope.message = gettext('There was a problem, members not saved.');
                    });
                };
            }
        };
    }]);
});
