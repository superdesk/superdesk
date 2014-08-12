define([
    'angular',
    'moment'
], function(angular, moment) {
    'use strict';

    var TIMEOUT = 5000;

    return angular.module('superdesk.notification', ['superdesk.data'])
    .run(['$rootScope', '$timeout', '$q', 'api',
    	function($rootScope, $timeout, $q, api) {
			var last, timeout;

			// get last notification and use it to query changes after
			function getLast() {
				if (last) {
					return $q.when(last);
				}

				return api.notification.query({size: 1}).then(function(items) {
					return items._items.length ? items._items[0]._created : $q.reject(); // no notifications yet
				});
			}

			function pool() {
				getLast().then(function(_last) {
					var q = {where: {_created: {$gt: _last}}};
					api.notification.query(q).then(function(items) {
						var notifications = {};
						_.each(items._items, function(item) {
							_.each(item.changes, function(change, name) {
								var current = notifications[name];
								if (current == null) {
									current = notifications[name] = {
										created: 0,
										updated: 0,
										deleted: 0,
										keys: {}
									};
								}
								current.created += change.created;
								current.updated += change.updated;
								current.deleted += change.deleted;
								if (change.keys !== undefined) {
									_.each(change.keys, function(key) {
										current.keys[key] = true;
									});
								}
							});
						});

						last = items._items.length ? items._items[0]._created : _last;

						_.each(notifications, function(changes, name) {
							$rootScope.$broadcast('changes in ' + name, changes);
						});

						timeout = $timeout(pool, TIMEOUT);
					}, function() {
						// In case of error we will try in 10 seconds.
						timeout = $timeout(pool, TIMEOUT * 2);
					});
				});
			}

			function startPool() {
				timeout = $timeout(pool, TIMEOUT);
			}

			function stopPool() {
				if (timeout) {
					$timeout.cancel(timeout);
					timeout = null;
				}
			}

			$rootScope.$on('$routeChangeSuccess', startPool);
			$rootScope.$on('$locationChangeStart', stopPool);
		}]);
});
