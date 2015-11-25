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
            //filter['recipients.user_id'] = session.identity._id;
            filter = {'recipients.user_id': session.identity._id};

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
                        var recipients = item.recipients || {};
                        item._unread = !isRead(recipients, identity._id, true);
                        this.unread += item._unread ? 1 : 0;
                    }, this);
                }));
        };

        // mark an item as read
        this.markAsRead = function(notification) {
            var _notification = angular.extend({}, notification);
            var recipients = notification.recipients;
            var recipient = _.find(recipients, {'user_id': session.identity._id});
            if (recipient && !recipient['read']) {
                recipient['read'] = true;
                return api('activity').save(_notification, {'recipients': recipients}).then(angular.bind(this, function() {
                    this.unread = _.max([0, this.unread - 1]);
                    notification._unread = null;
                }));
            }
        };

        function isUserInRecipients(activity, user_id) {
            return _.find(activity, {'user_id': session.identity._id});
        }

        function isRead(activity, user_id) {
            var userReadRecord = isUserInRecipients(activity, user_id);
            return userReadRecord && userReadRecord['read']
        }

        function isCurrentUser(extras) {
            var dest = extras._dest || [];
            return session.identity && isUserInRecipients(dest, session.identity._id);
        }

        this.reload();
        var reload = angular.bind(this, this.reload);
        session.getIdentity().then(function() {
            if (session.identity.user_type === 'user') {
                $rootScope.$on('user:mention', function(_e, extras) {
                    if (isCurrentUser(extras)) {
                        $timeout(reload, UPDATE_TIMEOUT, false);
                    }
                });
            } else {
                $rootScope.$on('activity', function(_e, extras) {
                    if (isCurrentUser(extras)) {
                        $timeout(reload, UPDATE_TIMEOUT, false);
                    }
                });
            }
        });
    }

    DeskNotificationsService.$inject = ['$rootScope', '$timeout', 'api', 'session', 'moment'];
    function DeskNotificationsService($rootScope, $timeout, api, session, moment) {

        var INIT_TIMEOUT = 1000,
            UPDATE_TIMEOUT = 500;

        this._items = null;
        this.unread = {};

        /**
         * Get notifications filter for current user based on his type
         *
         * for type 'user' it will only get content notifications,
         * for administrators it will get all notifications (eg. ingest).
         *
         * @return {Object}
         */
        function getFilter() {
            var date = moment().subtract(1, 'days').utc();
            //var filter = {};
            var filter = {'recipients.desk_id': {$exists: true}};
            //filter._created = {$gte: new Date(date.format())};
            //var filter = {'_created': {$gte: new Date(date.toISOString())}, 'recipients.desk_id': {$exists: true}};
            return filter;
        }

        this.getUnreadCount = function(deskId) {
            return this.unread[deskId];
        };

        this.getNotifications = function(deskId) {
            return this._items[deskId];
        };
        
        // reload notifications
        this.reload = function() {
            var criteria = {
                where: getFilter(),
                embedded: {user: 1, item: 1},
                max_results: 20
            };

            return api.query('activity', criteria)
                .then(angular.bind(this, function(response) {
                    this._items = {};
                    this.unread = {};
                    _.each(response._items, function(item) {
                        var recipients = item.recipients || {};
                        _.each(recipients, function(recipient) {
                            if (recipient.desk_id) {
                                if (!this.unread[recipient.desk_id]) {
                                    this._items[recipient.desk_id] = [];
                                    this.unread[recipient.desk_id] = 0;
                                }

                                this._items[recipient.desk_id].push(item)
                                this.unread[recipient.desk_id] += !isRead(recipients, recipient.desk_id, true) ? 1 : 0;
                            }
                        }, this);
                    }, this);
                }));
        };

        // mark an item as read
        this.markAsRead = function(notification, deskId) {
            var _notification = angular.extend({}, notification);
            var recipients = notification.recipients;
            var recipient = _.clone(_.find(recipients, {'desk_id': deskId}));
            if (recipient && !recipient['read']) {
                recipient['read'] = true;
                recipient['user_id'] = session.identity._id;
                return api('activity').save(_notification, {'recipients': recipients}).then(angular.bind(this, function() {
                    this.unread = _.max([0, this.unread - 1]);
                    notification._unread = null;
                }));
            }
        };

        function isDeskInRecipients(activity, deskId) {
            return _.find(activity, {'desk_id': deskId});
        }

        function isRead(activity, deskId) {
            var deskReadRecord = isDeskInRecipients(activity, deskId);
            return deskReadRecord && deskReadRecord['read']
        }

        this.reload();
        var reload = angular.bind(this, this.reload);
        $rootScope.$on('desk:mention', reload);
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
        .service('deskNotifications', DeskNotificationsService)
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
