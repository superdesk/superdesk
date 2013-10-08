define([
    'angular',
], function(angular) {
    'use strict';

    angular.module('superdesk.profile.resources', []).
        factory('usersResource', function( $resource) {
            return $resource('scripts/superdesk/profile/static-resources/users.json');
        }).
        factory('activityResource', function( $resource) {
            return $resource('scripts/superdesk/profile/static-resources/activity.json');
        })
});