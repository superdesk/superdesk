define([
    'lodash',
    './baseList'
], function(_, BaseListController) {
    'use strict';

    ArchiveListController.$inject = ['$scope', '$injector', '$timeout', 'superdesk', 'api'];
    function ArchiveListController($scope, $injector, $timeout, superdesk, api) {
        $injector.invoke(BaseListController, this, {$scope: $scope});

        $scope.createdMedia = {
            items: []
        };

        $scope.type = 'archive';

        $scope.openUpload = function() {
            superdesk.intent('upload', 'media').then(function(items) {
                // todo: put somewhere else
                $scope.createdMedia.items.unshift.apply($scope.createdMedia.items, items);
            });
        };

        this.fetchItems = function(criteria) {
        	var last = null;
        	(function tick() {
        		var q = null;
        		if(last != null){
        			q = {where: JSON.stringify({"_created": {"$gte": last.replace("+", "%2B")}})};
        		}
        		api.notification.query(q).then(function(items){
        			var notifications = {};
        			if(last != null){
	        			_.each(items._items, function(item) {
	        				for (var key in item.changes) {
	        					var current = notifications[key];
	        					if(current == null){
	        						current = notifications[key] = {created: 0, updated: 0, deleted: 0};
	        					};
	        					var change = item.changes[key];
	        					current.created += change.created;
	        					current.updated += change.updated;
	        					current.deleted += change.deleted;
		        			}
	        			});
        			}
	        		_.each(items._items, function(item) {
        				if(last == null){
        					last = item._created;
        				}else{
        					if(last < item._created){
        						last = item._created;
        					}
        				}
                    });
	        		if (notifications.length > 0){
	        			alert(JSON.stringify(notifications));
	        		}
        			if("media_archive" in notifications){
        				alert("UPDATING");
        				api.archive.query(criteria).then(function(items) {
        	                $scope.items = items;
        	                $scope.createdMedia = {
        	                    items: []
        	                };
        	            });
        				alert("UPDATED");
        			}
            		$timeout(tick, 2000);
        		});
            })();
        	
            api.archive.query(criteria).then(function(items) {
                $scope.items = items;
                $scope.createdMedia = {
                    items: []
                };
            });
        };
    }

    return ArchiveListController;
});
