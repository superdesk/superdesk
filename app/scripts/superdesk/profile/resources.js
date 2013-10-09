define([
    'angular',
], function(angular) {
    'use strict';

    angular.module('superdesk.profile.resources', ['superdesk.server']).
        factory('usersResource', function( $resource) {
            return $resource('scripts/superdesk/profile/static-resources/users.json');
        }).
        factory('activityResource', function( $resource) {
            return $resource('scripts/superdesk/profile/static-resources/activity.json');
        }).
        service('profileService', function(server) {
            return {
                /**
                 * Get user for given username
                 *
                 * @param {string} username
                 * @return {object} user
                 */
                getUserByUsername: function(username) {
                    return server.readItem('users', username);
                },

                /**
                 * Get user activity feed for given user
                 *
                 * @param {object} user
                 * @return {object} activity
                 */
                getUserActivity: function(user) {
                    return server.readList('activity', {
                        where: {user: user._id},
                        sort: '[("created", -1)]',
                        embedded: {user: 1}
                    });
                }
            };
        });
});