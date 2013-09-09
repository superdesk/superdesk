define(['angular'], function(angular) {
    'use strict';

    return ['$scope', '$location', '$routeParams', 'items',
    function($scope, $location, $routeParams, items) {
        $scope.items = items;

        $scope.query = 'q' in $routeParams ? $routeParams.q : null;
        $scope.search = function(query) {
        	if (query && query.length > 2) {
                $location.search('q', query);
                $location.search('skip', null);
        	} else if (query.length === 0) {
        		$location.search('q', null);
                $location.search('skip', null);
        	}
        };

        $scope.edit = function(item) {
            $scope.editItem = item;
        };

        $scope.closeEdit = function() {
            $scope.editItem = null;
        };
    }];
});
