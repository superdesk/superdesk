(function() {
    'use strict';

    UserNotificationsService.$inject = ['$rootScope', '$timeout', 'api', 'session'];
    function UserNotificationsService($rootScope, $timeout, api, session) {
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
                embedded: {user: 1}
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
                            // pass
                        }
                    }, this);
                }));
        };

        // mark an item as read
        this.markAsRead = function(notification) {
            var users = notification.read;
            users[session.identity._id] = 1;
            return api('activity').save(notification, {read: users}, {embedded: {user: 1}}).then(angular.bind(this, function() {
                this.unread = _.max([0, this.unread - 1]);
            }));
        };

        function isCurrentUserNotification(extras) {
            var dest = extras._dest || {};
            return !dest[session.identity._id];
        }

        // reload on activity notification
        $rootScope.$on('activity', angular.bind(this, function(_e, extras) {
            if (isCurrentUserNotification(extras)) {
                $timeout(angular.bind(this, this.reload));
            }
        }));

        // init
        $timeout(angular.bind(this, this.reload));
    }

    /**
     * Schedule marking an item as read. If the scope is destroyed before it will keep it unread.
     */
    MarkAsReadDirective.$inject = ['userNotifications', '$timeout'];
    function MarkAsReadDirective(userNotifications, $timeout) {
        var TIMEOUT = 3000;
        return {
            link: function(scope) {
                var timeout = $timeout(function() {
                    userNotifications.markAsRead(scope.notification);
                }, TIMEOUT);

                scope.$on('$destroy', function() {
                    $timeout.cancel(timeout);
                });
            }
        };
    }

    angular.module('superdesk.menu', [])

        .service('userNotifications', UserNotificationsService)
        .directive('sdMarkAsRead', MarkAsReadDirective)

        // set flags for other directives
        .directive('sdSuperdeskView', function() {
            return {
                templateUrl: 'scripts/superdesk/menu/views/superdesk-view.html',
                controller: function() {
                    this.flags = {
                        menu: false,
                        notifications: false
                    };
                },
                link: function(scope, elem, attrs, ctrl) {
                    scope.flags = ctrl.flags;
                }
            };
        })

        .directive('sdMenuWrapper', ['$route', 'superdesk', 'betaService', 'userNotifications',
        function($route, superdesk, betaService, userNotifications) {
            return {
                require: '^sdSuperdeskView',
                templateUrl: 'scripts/superdesk/menu/views/menu.html',
                link: function(scope, elem, attrs, ctrl) {

                    scope.currentRoute = null;
                    scope.flags = ctrl.flags;
                    scope.menu = _.values(_.where(superdesk.activities, {category: superdesk.MENU_MAIN}));

                    scope.toggleMenu = function() {
                        ctrl.flags.menu = !ctrl.flags.menu;
                    };

                    scope.toggleNotifications = function() {
                        ctrl.flags.notifications = !ctrl.flags.notifications;
                    };

                    scope.toggleBeta = function() {
                        betaService.toggleBeta();
                    };

                    function setActiveMenuItem(route) {
                        _.each(scope.menu, function(activity) {
                            activity.isActive = route && route.href &&
                                route.href.substr(0, activity.href.length) === activity.href;
                        });
                    }

                    scope.$on('$locationChangeStart', function() {
                        ctrl.flags.menu = false;
                    });

                    scope.$watch(function() {
                        return $route.current;
                    }, function(route) {
                        scope.currentRoute = route || null;
                        setActiveMenuItem(scope.currentRoute);
                    });

                    scope.notifications = userNotifications;
                }
            };
        }])

        .directive('sdNotifications', function() {
            return {
                require: '^sdSuperdeskView',
                templateUrl: 'scripts/superdesk/menu/views/notifications.html',
                link: function(scope, elem, attrs, ctrl) {
                    scope.flags = ctrl.flags;
                }
            };
        });
})();
