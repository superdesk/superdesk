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

                scope.$watch('currentStep', function(step) {
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
                        WizardHandler.wizard().next();
                    }, function(response) {
                        scope.message = gettext('There was a problem, desk not created/updated.');
                    });
                };
            }
        };
    }])
    .directive('sdDeskeditStages', ['gettext', 'api', 'WizardHandler', 'desks',
        function(gettext, api, WizardHandler, desks) {
        return {

            link: function(scope, elem, attrs) {

                scope.$watch('currentStep', function(step, previous) {
                    if (step === 'stages') {

                        scope.stages = [];
                        scope.newStage = {
                            show: false,
                            model: null
                        };
                        scope.message = null;

                        if (scope.desk.edit && scope.desk.edit._id) {
                            scope.message = null;
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
                        scope.message = gettext('Savinig...');
                        api('content_view').save({}, {name: scope.newStage.model, desk: scope.desk.edit._id})
                        .then(function(item) {
                            scope.stages.push(item);
                            scope.newStage.model = null;
                            scope.newStage.show = false;
                            scope.message = gettext('Stage added successfully.');
                        }, function(response) {
                            console.log(response);
                            scope.message = gettext('There was a problem, stage not added.');
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
