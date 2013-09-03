define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'ItemLoader', function($scope, ItemLoader) {
        $scope.item = ItemLoader($scope.ref.residRef);
    }];
});