define(['angular'], function(angular) {
    'use strict';

    return function($scope, ItemListLoader) {
        var params = {
            sort: '[("firstCreated", -1)]',
            where: angular.toJson({'itemClass': 'icls:text'})
        };

        $scope.items = ItemListLoader(params);
    };
});
