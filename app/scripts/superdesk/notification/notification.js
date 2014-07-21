define([
    'angular',
    'require',
    '../api/api-service'
], function(angular, require) {
    'use strict';

    var TIMEOUT = 8000;

    return angular.module('superdesk.notification', [ 'superdesk.data' ])
    .run(['$rootScope', '$timeout', 'api',
    	function($rootScope, $timeout, api) {
			var last, timeout;

			function pool() {
				var q = null;
				if (last != null) {
					q = {where: {'_created': {'$gt': last}}};
				}
				api.notification.query(q).then(function(items) {
					var notifications = {};
					if (last != null) {
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
								if (change.keys != undefined){
									_.each(change.keys, function(key){
										current.keys[key] = true;
									});
								}
							});
						});
					}
					_.each(items._items, function(item) {
						if (last == null) {
							last = item._created;
						} else {
							if (last < item._created) {
								last = item._created;
							}
						}
					});
					_.each(notifications, function(changes, name) {
						$rootScope.$broadcast('changes in ' + name, changes);
					});
					timeout = $timeout(pool, TIMEOUT);
				}, function() {
					// In case of error we will try in 10 seconds.
					timeout = $timeout(pool, TIMEOUT * 2);
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
