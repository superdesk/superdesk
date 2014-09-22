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
                selectedDesk: '=desk'
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
    .directive('sdFocusInput', [ '$timeout', function($timeout) {
        return {
            link: function(scope, elem, attrs) {
                elem.click(function() {
                     $timeout(function() {
                        elem.parent().find('input').focus();
                    });
                });
            }
        };
    }])
    .directive('sdDeskeditBasic', ['gettext', 'notify', 'api', 'WizardHandler', function(gettext, notify, api, WizardHandler) {
        return {

            link: function(scope, elem, attrs) {

                var _desk = null;

                scope.$watch('currentStep', function(step) {
                    if (step === 'general') {
                        scope.edit(scope.desk.edit);
                    }
                });

                scope.edit = function(desk) {
                    scope.desk.edit = _.create(desk);
                    _desk = desk || {};
                };

                scope.save = function(desk) {
                    notify.info(gettext('saving...'));
                    var _new = desk._id ? false : true;
                    api.desks.save(_desk, scope.desk.edit).then(function(result) {
                        notify.pop();
                        if (_new) {
                            notify.success(gettext('New Desk created.'));
                            _.extend(desk, result);
                            scope.desks._items.unshift(scope.desk.edit);
                        } else {
                            notify.success(gettext('Desk settings updated.'));
                            _.extend(_desk, result);
                        }
                        WizardHandler.wizard().next();
                    }, function(response) {
                        notify.pop();
                        notify.error(gettext('There was a problem, desk not created/updated.'));
                    });
                };
            }
        };
    }])
    .directive('sdDeskeditStages', ['gettext', 'notify', 'api', 'WizardHandler', 'desks',
        function(gettext, notify, api, WizardHandler, desks) {
        return {

            link: function(scope, elem, attrs) {

                scope.stages = [];

                scope.newStage = {
                    show: false,
                    model: null
                };

                scope.$watch('currentStep', function(step, previous) {
                    if (step === 'stages') {
                        if (scope.desk.edit && scope.desk.edit._id) {
                            api('content_view').query({where: {desk: scope.desk.edit._id}})
                            .then(function(result) {
                                scope.stages = result._items;
                            });
                        } else {
                            WizardHandler.wizard().goTo(previous);
                        }
                    }
                });

                scope.previous = function() {
                    WizardHandler.wizard().previous();
                };

                scope.done = function() {
                    WizardHandler.wizard().finish();
                };

                scope.saveOnEnter = function($event) {
                    if ($event.keyCode === 13) {
                        api('content_view').save({}, {name: scope.newStage.model, desk: scope.desk.edit._id})
                        .then(function(item) {
                            scope.stages.push(item);
                            scope.newStage.model = null;
                            scope.newStage.show = false;
                        }, function(response) {
                            console.log(response);
                        });
                        return false;
                    }
                };

                scope.remove = function(stage) {
                    //stil not suported in API

                    // api('content_view').remove(stage)
                    // .then(function(result) {
                    //     _.remove(scope.stages, stage);
                    // }, function(response) {
                    //     console.log(response);
                    // });
                };
            }
        };
    }]);
});
