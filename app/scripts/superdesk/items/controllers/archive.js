define([
    'angular',
], function(angular) {
    return [
        '$scope',
        '$routeParams',
        'ItemListLoader',
        function($scope, $routeParams, ItemListLoader) {
            $scope.params = angular.extend({
                itemClass: 'icls:picture,icls:text',
                skip: 0,
                limit: 50
            }, $routeParams);

            $scope.items = ItemListLoader($scope.params);

            $scope.edit = function(item) {
                $scope.editItem = item;
            };

            $scope.closeEdit = function() {
                $scope.editItem = null;
            };
        }
    ];
});