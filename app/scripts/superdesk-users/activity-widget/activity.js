define([
    'angular',
    'require'
], function(angular, require) {
    'use strict';

    angular.module('superdesk.widgets.activity', ['superdesk.dashboard.widgets'])
        .config(['widgetsProvider', function(widgets) {
            widgets.widget('activity', {
                label: 'Activity Log',
                multiple: true,
                max_sizex: 2,
                max_sizey: 2,
                sizex: 1,
                sizey: 2,
                thumbnail: require.toUrl('./thumbnail.png'),
                template: require.toUrl('./widget-activity.html'),
                configurationTemplate: require.toUrl('./configuration.html'),
                configuration: {maxItems: 5},
                description: 'Activity log widget'
            });
        }]).controller('ActivityController', ['$scope', 'profileService',
        function ($scope, profileService) {
        	var page = 1;
        	var current_config = null;

        	function refresh(config) {
        		current_config = config;
	            profileService.getUserActivityFiltered(config.maxItems).then(function(list) {
	            	$scope.activityFeed = list;
	            });

	            $scope.loadMore = function() {
	                page++;
	                profileService.getUserActivityFiltered(config.maxItems, page).then(function(next) {
	                    Array.prototype.push.apply($scope.activityFeed._items, next._items);
	                    $scope.activityFeed._links = next._links;
	                });
	            };
        	}

        	$scope.$on('changes in activity', function() {
        		if (current_config) {
        			refresh(current_config);
        		}
        	});

            $scope.$watch('widget.configuration', function(config) {
                page = 1;
                if (config) {
                    refresh(config);
                }
            }, true);
        }]).controller('ActivityConfigController', ['$scope',
        function ($scope) {
            $scope.notIn = function(haystack) {
                return function(needle) {
                    return haystack.indexOf(needle) === -1;
                };
            };
        }]);
});
