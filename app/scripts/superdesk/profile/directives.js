define([
    'jquery',
    'angular',
    './resources'
], function($, angular) {
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
                link: function(scope, element, attrs) {
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
                link: function(scope, element, attrs) {
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
                link: function(scope, element, attrs) {
                    var scopeCaller = false;
                    element.bind('click', function() {
                        scope.$apply(function(){
                            scope.check = !scope.check;
                            scopeCaller=true;
                        });
                    });
                    scope.$watch('check', function() {
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
                require: 'ngModel',
                link: function(scope, element, attrs, ngModel) {
                    var maxResults = 5;
                    var page = 1;

                    ngModel.$render = function() {
                        profileService.getUserActivity(ngModel.$viewValue, maxResults).then(function(list) {
                            scope.activityFeed = list;
                        });
                    };

                    scope.loadMore = function() {
                        page++;
                        profileService.getUserActivity(ngModel.$viewValue, maxResults, page).then(function(next) {
                            Array.prototype.push.apply(scope.activityFeed.items, next.items);
                            scope.activityFeed.links = next.links;
                        });
                    };
                }
            };
        });
});