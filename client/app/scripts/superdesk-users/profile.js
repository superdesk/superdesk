(function() {
    'use strict';

    ProfileService.$inject = ['api'];
    function ProfileService(api) {

        var RESOURCE = 'activity';

        /**
         * Get all activity of single user, being it content related or not
         *
         * @param {Object} user
         * @param {number} maxResults
         * @param {number} page
         * @return {Promise}
         */
        this.getUserActivity = function(user, maxResults, page) {
            var q = {
                where: {user: user._id},
                sort: '[(\'_created\',-1)]',
                embedded: {user: 1, item: 1}
            };

            if (maxResults) {
                q.max_results = maxResults;
            }

            if (page > 1) {
                q.page = page;
            }

            return api.query(RESOURCE, q);
        };

        /**
         * Get activity of all users related to content
         *
         * This will return activity like item created/updated, but not user.updated.
         *
         * @param {number} maxResults
         * @param {number} page
         * @return {Promise}
         */
        this.getAllUsersActivity = function(maxResults, page) {
            var q = {
                sort: '[(\'_created\',-1)]',
                where: {user: {$exists: true}, item: {$exists: true}},
                embedded: {user: 1, item: 1}
            };

            if (maxResults) {
                q.max_results = maxResults;
            }

            if (page > 1) {
                q.page = page;
            }

            return api.query(RESOURCE, q);
        };
    }

    angular.module('superdesk.users.profile', ['superdesk.api', 'superdesk.users'])

        .service('profileService', ProfileService)

        .config(['superdeskProvider', 'assetProvider', function(superdeskProvider, asset) {
            superdeskProvider.activity('/profile/', {
                label: gettext('My Profile'),
                controller: 'UserEditController',
                templateUrl: asset.templateUrl('superdesk-users/views/edit.html'),
                resolve: {
                    user: ['session', 'api', function(session, api) {
                        return session.getIdentity().then(function(identity) {
                            return api.get(identity._links.self.href);
                        });
                    }]
                }
            });
        }])

        .directive('sdUserActivity', ['profileService', 'asset', function(profileService, asset) {
            return {
                restrict: 'A',
                replace: true,
                templateUrl: asset.templateUrl('superdesk-users/views/activity-feed.html'),
                scope: {
                    user: '='
                },
                link: function(scope, element, attrs) {
                    var page = 1;
                    var maxResults = 5;
                    scope.max_results = maxResults;

                    scope.$watch('user', function() {
                        profileService.getUserActivity(scope.user, maxResults).then(function(list) {
                            scope.activityFeed = list;
                        });
                    });

                    scope.loadMore = function() {
                        page++;
                        profileService.getUserActivity(scope.user, maxResults, page).then(function(next) {
                            Array.prototype.push.apply(scope.activityFeed._items, next._items);
                            scope.activityFeed._links = next._links;
                            scope.max_results += maxResults;
                        });
                    };
                }
            };
        }]);
})();
