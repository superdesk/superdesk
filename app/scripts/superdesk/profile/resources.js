define([
    'angular'
], function(angular) {
    'use strict';

    angular.module('superdesk.profile.resources', ['superdesk.server']).
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
                 * @param {number} maxResults
                 * @param {number} page
                 * @return {object} activity
                 */
                getUserActivity: function(user, maxResults, page) {
                    var params = {
                        where: {user: user._id},
                        sort: '[("created", -1)]',
                        embedded: {user: 1},
                    };

                    if (maxResults) {
                        params.max_results = maxResults;
                    }

                    if (page > 1) {
                        params.page = page;
                    }

                    return server.list('activity', params);
                }
            };
        });
});