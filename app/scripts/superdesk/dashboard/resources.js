define([
    'angular',
    'moment'
], function(angular) {
    'use strict';

    angular.module('superdesk.dashboard.resources', ['ngResource']).
        factory('worldclock', function( $resource) {
            return  $resource('scripts/superdesk/dashboard/static-resources/clock.json');
        })
        
});