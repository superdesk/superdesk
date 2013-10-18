define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'itemLoader', function($scope, itemLoader) {
        $scope.item = itemLoader($scope.ref.residRef);
    }];
});