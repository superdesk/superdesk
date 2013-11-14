define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'items', 'em',
    function($scope, items, em) {

        $scope.items = items;

        $scope.archive = function(item) {
            em.create('archive', item).then(function() {
                item.archived = true;
                item.archiving = false;
            });
            item.archiving = true;
        };

    }];
});
