define(['angular'], function(angular) {
    'use strict';

    var TEXT_CLASS = 'icls:text';

    return function($scope, ItemListLoader) {
        $scope.params = {
            sort: '[("firstCreated", -1)]',
            where: {itemClass: TEXT_CLASS},
            page: null
        };

        $scope.fetch = function(options) {
        	angular.extend($scope.params, options);
        	$scope.items = ItemListLoader($scope.params);
        };

        $scope.prev = function() {
            var prev = $scope.params.page <= 2 ? null : $scope.params.page - 1;
            $scope.fetch({page: prev});
        };

        $scope.next = function() {
            var next = $scope.params.page < 2 ? 2 : $scope.params.page + 1;
            $scope.fetch({page: next});
        }

        $scope.search = function(query) {
        	if (query) {
        		$scope.fetch({
        			where: {headline: query, itemClass: TEXT_CLASS},
        			page: null
        		});
        	} else {
        		$scope.fetch({
        			where: {itemClass: TEXT_CLASS},
        			page: null
        		});
        	}
        };

        $scope.fetch();
    };
});
