define(['angular'], function(angular) {
    'use strict';

    var TEXT_CLASS = 'icls:text';

    return function($scope, ItemListLoader) {
        $scope.params = {
            sort: '[("firstCreated", -1)]',
            where: {itemClass: TEXT_CLASS},
            page: 0
        };

        $scope.fetch = function(options) {
        	angular.extend($scope.params, options);
        	$scope.items = ItemListLoader($scope.params);
        };

        $scope.search = function(query) {
        	if (query) {
        		$scope.fetch({
        			where: {headline: /query/, itemClass: TEXT_CLASS},
        			page: 0
        		});
        	} else {
        		$scope.fetch({
        			where: {itemClass: TEXT_CLASS},
        			page: 0
        		});
        	}
        };

        $scope.fetch();
    };
});
