define(['angular'], function(angular) {
    'use strict';

    var module = angular.module('superdesk.users.services', []);

    module.service('profileService', ['api', function(api) {
        /**
         * User profile service
         */
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
                var q = {
                    where: {user: user._id},
                    sort: "[('_created',-1)]",
                    embedded: {user: 1}
                };

                if (maxResults) {
                    q.max_results = maxResults;
                }

                if (page > 1) {
                    q.page = page;
                }

                return api.activity.query(q);
            },
            
            /**
             * Get filtered user activity feed
             *
             * @param {object} user
             * @param {number} maxResults
             * @param {number} page
             * @return {object} activity
             */
            getUserActivityFiltered: function(maxResults, page) {
                var q = {
                    sort: "[('_created',-1)]",
                    embedded: {user: 1}
                };

                if (maxResults) {
                    q.max_results = maxResults;
                }

                if (page > 1) {
                    q.page = page;
                }

                return api.activity.query(q);
            }
        };
    }]);
});
