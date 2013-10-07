define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    angular.module('superdesk.profile.directives', []).
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
        directive('activity', function($compile) {
            return {
                restrict: 'E',
                replace: true,
                translude : true,
                templateUrl : 'scripts/superdesk/profile/views/single-activity.html',
                scope: {
                    feed : "=",
                },
                link: function(scope, element, attrs, controller) {
                    scope.$watch('feed.content', function(newContent) {
                      element.find('.activity-content').html($compile(newContent)(scope));
                    });
                }
            };
        }).
        directive('activityFeed', function() {
            return {
                restrict: 'E',
                replace: true,
                templateUrl : 'scripts/superdesk/profile/views/activity-feed.html',
                scope: {
                    feedsource : "=",
                }
            };
        })

});