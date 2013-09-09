define(['angular'], function(angular) {
    'use strict';

    return ['$scope', '$location', 'items',
    function($scope, $location, items) {
        $scope.items = items;

        $scope.open = function(path) {
            $location.path(path);
        };

        $scope.edit = function(item) {
            $scope.editItem = item;
        };

        $scope.closeEdit = function() {
            $scope.editItem = null;
        };
    }];
});
