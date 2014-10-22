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

                var _desk = null;

                scope.$watch('step.current', function(step) {
                    if (step === 'general') {
                        scope.edit(scope.desk.edit);
                        scope.message = null;
                    }
                });

                scope.edit = function(desk) {
                    scope.desk.edit = _.create(desk);
                    _desk = desk || {};
                };

                scope.save = function(desk) {
                    scope.message = gettext('Saving...');
                    var _new = desk._id ? false : true;
                    api.desks.save(_desk, desk).then(function() {
                        if (_new) {
                            scope.edit(_desk);
                            scope.desks._items.unshift(_desk);
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
                    scope.editStage = null;
                };

                scope.remove = function(stage) {
                    api('stages').remove(stage)
                        .then(function(result) {
                            _.remove(scope.stages, stage);
                        });
                };
            }
        };
    }])
    .directive('sdDeskeditPeople', ['gettext', 'api', 'WizardHandler', 'desks',
        function(gettext, api, WizardHandler, desks) {
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
                            desks.initialize().then(function() {
                                scope.deskMembers = desks.deskMembers[scope.desk.edit._id] || [];
                                scope.users = desks.users._items;
                                generateSearchList();
                            });
                        } else {
                            WizardHandler.wizard('desks').goTo(previous);
                        }
                    }
                });

                function generateSearchList() {
                    scope.membersToSelect = _.difference(scope.users, scope.deskMembers);
                }

                scope.add = function(user) {
                    scope.deskMembers.push(user);
                    generateSearchList();
                    scope.search = null;
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
                        WizardHandler.wizard('desks').finish();
                    }, function(response) {
                        scope.message = gettext('There was a problem, members not saved.');
                    });
                };
            }
        };
    }]);
});
