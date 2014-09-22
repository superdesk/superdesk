(function() {
    'use strict';

    UserNotificationsService.$inject = ['$rootScope', '$timeout', 'api', 'session'];
    function UserNotificationsService($rootScope, $timeout, api, session) {

        var INIT_TIMEOUT = 500,
            UPDATE_TIMEOUT = 300;

        this._items = null;
        this.unread = 0;

        function getFilter() {
            var filter = {},
                user_key = 'read.' + session.identity._id;
            filter[user_key] = {$exists: true};
            return filter;
        }

        // reload notifications
        this.reload = function() {
            var criteria = {
                where: getFilter(),
                embedded: {user: 1, item: 1}
            };

            return api('activity')
                .query(criteria)
                .then(angular.bind(this, function(response) {
                    this._items = response._items;
                    this.unread = 0;
                    _.each(this._items, function(item) {
                        try {
                            item._unread = !item.read[session.identity._id];
                            this.unread += item._unread ? 1 : 0;
                        } catch (err) {
                            // .read not set
                        }
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
            return !dest[session.identity._id];
        }

        // reload on activity notification
        $rootScope.$on('activity', angular.bind(this, function(_e, extras) {
            if (isCurrentUser(extras)) {
                $timeout(angular.bind(this, this.reload), UPDATE_TIMEOUT);
            }
        }));

        // init
        $timeout(angular.bind(this, this.reload), INIT_TIMEOUT);
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

    angular.module('superdesk.menu.notifications', [])

        .service('userNotifications', UserNotificationsService)
        .directive('sdMarkAsRead', MarkAsReadDirective)

        .directive('sdNotifications', function() {
            return {
                require: '^sdSuperdeskView',
                templateUrl: 'scripts/superdesk/menu/notifications/views/notifications.html',
                link: function(scope, elem, attrs, ctrl) {
                    scope.flags = ctrl.flags;
                }
            };
        });
})();
