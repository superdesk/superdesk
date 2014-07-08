define([
    'angular',
    'require',
    '../api/api-service'
], function(angular, require) {
    'use strict';

    return angular.module('superdesk.notification', [ 'superdesk.data' ])
    .run(['$rootScope', '$timeout', 'api',
    	function($rootScope, $timeout, api) {
			var last = null;
			(function pool() {
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
										deleted: 0
									};
								}
								current.created += change.created;
								current.updated += change.updated;
								current.deleted += change.deleted;
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
					// Pool next notifications in 3 seconds.
					$timeout(pool, 34000);
				}, function() {
					// In case of error we will try in 10 seconds.
					$timeout(pool, 55000);
				});
			})();
		}]);
});
