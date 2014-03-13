define([
    'angular'
], function(angular) {
    'use strict';

    var module = angular.module('superdesk.directives');

    module.directive('sdNotifications', [ function() {
        return {
            templateUrl: 'scripts/superdesk/views/notifications.html',
            link: function(scope, elem, attrs) {

            }
        };
    }]);

});
