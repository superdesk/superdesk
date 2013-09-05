define(['angular'], function(angular) {
    return ['$scope', 'item', 'ItemService', function($scope, item, ItemService) {

        $scope.item = item;

        $scope.save = function(item) {
            ItemService.update(item);
        };
    }];
});