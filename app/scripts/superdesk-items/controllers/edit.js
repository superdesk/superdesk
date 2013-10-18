define(['angular'], function(angular) {
    'use strict';

    return ['$scope', '$location', 'item', 'ItemService',
    function($scope, $location, item, ItemService) {
        $scope.item = item;

        $scope.save = function(item) {
            ItemService.update(item);
        };

        $scope.close = function() {
            $location.path('/');
        };
    }];
});