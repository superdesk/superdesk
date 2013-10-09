define([
    'jquery',
    'angular',
    'moment',
    './resources'
], function($, angular, moment) {
    'use strict';

    angular.module('superdesk.profile.directives', ['superdesk.profile.resources']).
        directive('sdcheck', function() {
            return {
                restrict: 'E',
                replace: true,
                template : '<span class="sf-checkbox-custom" ng-class="{\'sf-checked\':check, \'privacy-switch-checkbox\' : privacy }" ></span>',
                scope: {
                    check : "=",
                    clickevent : "&", 
                    privacy : "="
                },
                link: function(scope, element, attrs, controller) {
                    element.bind('click', function() {
                        scope.$apply(function(){
                            scope.check = !scope.check;
                            scope.clickevent();
                        });
                    });
                }
            };
        }).
        directive('sdcheckW', function() {
            return {
                restrict: 'E',
                replace: true,
                template : '<span class="sf-checkbox-custom" ng-class="{\'sf-checked\':check, \'privacy-switch-checkbox\' : privacy }" ></span>',
                scope: {
                    check : "=",
                    clickevent : "&", 
                },
                link: function(scope, element, attrs, controller) {
                    element.bind('click', function() {
                        scope.clickevent();
                    });
                    
                }
            };
        }).
        directive('sdtoggle', function() {
            return {
                restrict: 'E',
                replace: true,
                template : '<div class="sf-toggle-custom" ng-class="{\'sf-checked\':check, \'on-off-toggle\' : onoff}"><div class="sf-toggle-custom-inner"></div></div>',
                scope: {
                    check : "=",
                    clickevent : "&",
                    onoff : "="
                },
                link: function(scope, element, attrs, controller) {
                    var scopeCaller = false;
                    element.bind('click', function() {
                        scope.$apply(function(){
                            scope.check = !scope.check;
                            scopeCaller=true;
                        });
                    });
                    scope.$watch('check', function(value) {
                        scopeCaller ? (scopeCaller = false, scope.clickevent()) : '';
                    });
                }
            };
        }).
        /**
         * sdActivityFeed is a widget rendering last activity for given user
         *
         * Usage:
         * <div sd-activity-feed ng-model="user"></div>
         *
         * Params:
         * @param {object} ngModel
         */
        directive('sdActivityFeed', function($rootScope, profileService) {
            return {
                restrict: 'A',
                replace: true,
                templateUrl : 'scripts/superdesk/profile/views/activity-feed.html',
                require: '?ngModel',
                link: function(scope, element, attrs, ngModel) {
                    ngModel.$render = function() {
                        scope.activity_list = profileService.getUserActivity(ngModel.$viewValue);
                    };
                }
            };
        }).
        /**
         * sdGroupDates directive will group list items by a date provided as a param.
         *
         * Usage:
         * <li ng-repeat="item in items" ng-model="item" sd-group-dates="updated">
         *
         * Params:
         * @param {object} ngModel
         * @param {string} sdGroupDates - model field to group by
         */
        directive('sdGroupDates', function() {
            var lastDate = null;
            var format = 'dddd';
            return {
                require: '?ngModel',
                link: function(scope, element, attrs, ngModel) {
                    ngModel.$render = function() {
                        var date = moment(ngModel.$viewValue[attrs.sdGroupDates]);
                        if (!lastDate || lastDate.format(format) != date.format(format)) {
                            element.before('<li class="date"><span>' + date.format('d MMMM') + '</span></li>');
                            lastDate = date;
                        }
                    };
                }
            }
        });
});