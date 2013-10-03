define([
    'jquery',
    'angular',
    'bootstrap_ui'
], function($, angular, bootstrap_ui) {
    'use strict';

    angular.module('superdesk.dashboard.directives', []).
        directive('sdWidget', function() {
            return {
                templateUrl : 'scripts/superdesk/dashboard/views/widget.html',
                replace: true,
                transclude: true,
                restrict: 'E',
                scope: {
                    widget: '=widget'
                },
                link: function(scope, element, attrs, controllers) {
                }
            };
        }).
        directive('sdWorldclock', function() {
            return {
                templateUrl : 'scripts/superdesk/dashboard/views/worldClock.html',
                replace: true,
                restrict: 'E',
                controller : 'WorldClockController', 
                link: function(scope, element, attrs, controllers) {
                    
                }
            };
        }).
        directive('sdClock', function() {
            return {
                templateUrl : 'scripts/superdesk/dashboard/views/worldClockBox.html',
                scope: { wtime: '=wtime' },
                replace: true,
                transclude: true,
                restrict: 'E',
                link: function(scope, element, attrs, controllers) {
                }
            };
        })
        
        
});