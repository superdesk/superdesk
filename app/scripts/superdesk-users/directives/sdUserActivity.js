define(function() {
    'use strict';

    /**
     * sdActivityFeed is a widget rendering last activity for given user
     *
     * Usage:
     * <div sd-activity-feed data-user="user"></div>
     */
    return ['profileService', function(profileService) {
        return {
            restrict: 'A',
            replace: true,
            templateUrl: 'scripts/superdesk-users/views/activity-feed.html',
            scope: {
                user: '='
            },
            link: function(scope, element, attrs) {
                var page = 1;
                var maxResults = 5;

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
                    });
                };
            }
        };
    }];
});
