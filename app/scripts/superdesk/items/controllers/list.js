define(['angular'], function(angular) {
    'use strict';

    return ['$scope', '$routeParams', 'ItemListLoader', function($scope, $routeParams, ItemListLoader) {
        $scope.params = angular.extend({
            itemClass: 'icls:composite',
            sort: '[("firstCreated", -1)]',
            skip: 0,
            limit: 25
        }, $routeParams);

        $scope.fetch = function(options) {
        	angular.extend($scope.params, options);
        	$scope.items = ItemListLoader($scope.params);
        };
        
        $scope.search = function(query) {
        	if (query && query.length > 2) {
        		$scope.fetch({
                    q: query,
        			skip: 0
        		});
        	} else if (query.length === 0) {
        		$scope.fetch({
                    q: null,
        			skip: 0
        		});
        	}
        };

        $scope.fetch();
    }];
});
