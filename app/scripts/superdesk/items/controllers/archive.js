define([
], function() {
    return [
        '$scope',
        'ItemListLoader',
        function($scope, ItemListLoader) {
            $scope.items = ItemListLoader({itemClass: 'icls:picture,icls:text', limit: 50});

            $scope.edit = function(item) {
                $scope.editItem = item;
            };

            $scope.closeEdit = function() {
                $scope.editItem = null;
            };
        }
    ];
});