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
                }
            };
        });
});