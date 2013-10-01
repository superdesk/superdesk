define([
    'jquery',
    'angular',
    'moment',
    'bootstrap_ui'
], function($, angular, moment) {
    'use strict';

    angular.module('superdesk.dashboard.directives', []).
        
        directive('sdClock', function() {
            return {
                templateUrl : 'scripts/superdesk/dashboard/views/clockbox.html',
                scope: { wtime: '=wtime' },
                replace: true,
                transclude: true,
                restrict: 'E',
                link: function(scope, element, attrs, controllers) {
                }
            };
        })
        
        
});