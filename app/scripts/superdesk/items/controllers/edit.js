define(['angular'], function(angular) {
    return ['$scope', '$routeParams', 'item', 'ItemService',
    function($scope, $routeParams, item, ItemService) {
        $scope.item = item;

        $scope.save = function(item) {
            ItemService.update(item);
        };

        if ('skip' in $routeParams) {
            $scope.closeLinkParams = '?skip=' + $routeParams.skip;
        }
    }];
});