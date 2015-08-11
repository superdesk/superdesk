(function() {
    'use strict';

    UserNotificationsService.$inject = ['$rootScope', '$timeout', 'api', 'session'];
    function UserNotificationsService($rootScope, $timeout, api, session) {

        var INIT_TIMEOUT = 1000,
            UPDATE_TIMEOUT = 500;

        this._items = null;
        this.unread = 0;

        /**
         * Get notifications filter for current user based on his type
         *
         * for type 'user' it will only get content notifications,
         * for administrators it will get all notifications (eg. ingest).
         *
         * @return {Object}
         */
        function getFilter() {
            var filter = {};
            var user_key = 'read.' + session.identity._id || 'all';
            filter[user_key] = {$exists: true};

            // filter out system messages for non-admin users
            if (session.identity.user_type === 'user') {
                filter.user = {$exists: true};
                filter.item = {$exists: true};
            }

            return filter;
        }

        // reload notifications
        this.reload = function() {
            if (!session.identity) {
                this._items = null;
                this.unread = 0;
                return;
            }

            var criteria = {
                where: getFilter(),
                embedded: {user: 1, item: 1},
                max_results: 8
            };

            return api.query('activity', criteria)
                .then(angular.bind(this, function(response) {
                    this._items = response._items;
                    this.unread = 0;
                    var identity = session.identity || {};
                    _.each(this._items, function(item) {
                        var read = item.read || {};
                        item._unread = !read[identity._id];
                        this.unread += item._unread ? 1 : 0;
                    }, this);
                }));
        };

        // mark an item as read
        this.markAsRead = function(notification) {
            var _notification = angular.extend({}, notification);
            var users = notification.read;
            users[session.identity._id] = 1;
            return api('activity').save(_notification, {read: users}).then(angular.bind(this, function() {
                this.unread = _.max([0, this.unread - 1]);
                notification._unread = null;
            }));
        };

        function isCurrentUser(extras) {
            var dest = extras._dest || {};
            return session.identity && !dest[session.identity._id];
        }

        var reload = angular.bind(this, this.reload);
        session.getIdentity().then(function() {
            $timeout(reload, INIT_TIMEOUT, false);
            $rootScope.$on('activity', function(_e, extras) {
                if (isCurrentUser(extras)) {
                    $timeout(reload, UPDATE_TIMEOUT, false);
                }
            });
        });
    }

    /**
     * Schedule marking an item as read. If the scope is destroyed before it will keep it unread.
     */
    MarkAsReadDirective.$inject = ['userNotifications', '$timeout'];
    function MarkAsReadDirective(userNotifications, $timeout) {
        var TIMEOUT = 5000;
        return {
            link: function(scope) {
                if (!scope.notification._unread) {
                    return;
                }

                var timeout = $timeout(function() {
                    userNotifications.markAsRead(scope.notification);
                }, TIMEOUT);

                scope.$on('$destroy', function() {
                    $timeout.cancel(timeout);
                });
            }
        };
    }

    angular.module('superdesk.menu.notifications', ['superdesk.asset'])

        .service('userNotifications', UserNotificationsService)
        .directive('sdMarkAsRead', MarkAsReadDirective)

        .directive('sdNotifications', ['asset', function(asset) {
            return {
                require: '^sdSuperdeskView',
                templateUrl: asset.templateUrl('superdesk/menu/notifications/views/notifications.html'),
                link: function(scope, elem, attrs, ctrl) {
                    scope.flags = ctrl.flags;
                }
            };
        }]);
})();
