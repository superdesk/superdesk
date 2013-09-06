define(['angular'], function(angular) {
    'use strict';

    var LIST_CLASS = 'icls:package';

    return ['$scope', '$routeParams', 'ItemListLoader', function($scope, $routeParams, ItemListLoader) {
        $scope.params = angular.extend({
            sort: '[("firstCreated", -1)]',
            where: {itemClass: LIST_CLASS},
            skip: 0,
            limit: 25
        }, $routeParams);

        $scope.links = {
            prev_link: null,
            next_link: null
        };

        function getPrevLink() {
            var skip = $scope.params.skip - $scope.params.limit;
            if (skip < 0) {
                skip = 0;
            }

            return skip === 0 ? '' : '?skip=' + skip;
        }

        function getNextLink() {
            var skip = parseInt($scope.params.skip) + parseInt($scope.params.limit);
            return '?skip=' + skip;
        }

        $scope.fetch = function(options) {
        	angular.extend($scope.params, options);
        	ItemListLoader($scope.params).
                then(function(items) {
                    $scope.items = items;
                    $scope.links.prev_link = items.has_prev ? getPrevLink() : null;
                    $scope.links.next_link = items.has_next ? getNextLink() : null;
                });
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
