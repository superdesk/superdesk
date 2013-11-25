define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'items', 'em', 'locationParams',
    function($scope, items, em, locationParams) {

        $scope.preview = function(item) {
            $scope.previewItem = item;
            $scope.previewSingle = item;

            if (item.type === 'composite') {
                $scope.previewSingle = null;
                $scope.previewItem.packageRefs = item.groups[_.findKey(item.groups,{id:'main'})].refs;
            }
        };

        $scope.archive = function(item) {
            em.create('archive', item).then(function(data) {
                delete item.archiving;
                item.archived = data.archived;
            });
            item.archiving = true;
        };

        $scope.items = items;

        if (locationParams.get('id')) {
            var item = _.find($scope.items._items, {_id: locationParams.get('id')});
            if (item) {
                $scope.preview(item);
            }
        }
    }];
});
