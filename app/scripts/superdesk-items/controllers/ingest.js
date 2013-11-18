define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'items', 'em',
    function($scope, items, em) {

        $scope.items = items;

        $scope.archive = function(item) {
            em.create('archive', item).then(function(data) {
                delete item.archiving;
                item.archived = data.archived;
            });
            item.archiving = true;
        };
    }];
});
