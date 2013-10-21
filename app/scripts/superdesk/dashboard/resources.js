define([
    'angular'
], function(angular) {
    'use strict';

    angular.module('superdesk.dashboard.resources', []).
       factory('widgetList', function( $resource) {
            return $resource('scripts/superdesk/dashboard/static-resources/widgets.json');
        });
});