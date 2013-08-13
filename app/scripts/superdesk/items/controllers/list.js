define(['angular'], function(angular) {
    'use strict';

    return function($scope, ItemsLoader) {
        $scope.items = ItemsLoader();
    };
});
