define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'items', 'em', 'locationParams', 'keyboardManager',
    function($scope, items, em, locationParams, keyboardManager) {

        $scope.items = items;
        
        $scope.context = false;     //status of context menu
        
        $scope.selectedIndex = -1;
        var previousitem = function() {
            if ($scope.selectedIndex>0) {
                $scope.selectedIndex--;
            }
            $scope.preview(items._items[$scope.selectedIndex],$scope.selectedIndex);
        };
        var nextitem = function() {
            if ($scope.selectedIndex<(items._items.length-1)) {
                $scope.selectedIndex++;
            }
            $scope.preview(items._items[$scope.selectedIndex],$scope.selectedIndex);
        };
        

        keyboardManager.bind('up', function() {
            previousitem();
            $scope.context = false;
        }, {
            'inputDisabled': true
        });
        keyboardManager.bind('down', function() {
            nextitem();
            $scope.context = false;
        }, {
            'inputDisabled': true
        });
        keyboardManager.bind('ctrl+a', function() {
            $scope.archive();
        });
        keyboardManager.bind('enter', function() {
            $scope.context = !$scope.context ;
            
        }, {
            'inputDisabled': true
        });

        $scope.preview = function(item, index) {
            if (item !== undefined) {
                $scope.selectedIndex = index;
                $scope.previewItem = item;
                $scope.previewSingle = item;

                if (item.type === 'composite') {
                    $scope.previewSingle = null;
                    $scope.previewItem.packageRefs = item.groups[_.findKey(item.groups,{id:'main'})].refs;
                }
            }
        };

        $scope.archive = function(archiveItem) {
            var item = archiveItem || items._items[$scope.selectedIndex];
            em.create('archive', item).then(function(data) {
                delete item.archiving;
                item.archived = data.archived;
            });
            item.archiving = true;
            $scope.context = false;
        };

        nextitem();

        if (locationParams.get('id')) {
            var item = _.find($scope.items._items, {_id: locationParams.get('id')});
            if (item) {
                $scope.preview(item);
            }
        }


    }];
});
