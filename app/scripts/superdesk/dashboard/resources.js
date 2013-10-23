define([
    'angular'
], function(angular) {
    'use strict';

    angular.module('superdesk.dashboard.resources', []).
        factory('widgetResource', ['$resource', function($resource) {
            return $resource(
                'scripts/superdesk/dashboard/static-resources/widgets.json', {},
                {get: {method: 'GET', isArray: true}}
            );
        }]);
});