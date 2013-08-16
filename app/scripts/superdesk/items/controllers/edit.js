define(['angular'], function(angular) {
    return ['$scope', 'item', function($scope, item) {
        $scope.item = item;
    }];
});