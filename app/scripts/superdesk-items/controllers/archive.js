define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'items',
    function($scope, items) {
        $scope.items = items;
    }];
});
