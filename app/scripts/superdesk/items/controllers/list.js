define(['angular'], function(angular) {
    'use strict';

    return ['$scope', '$location', 'items',
    function($scope, $location, items) {

        $scope.items = items;
        $scope.selectedItem = {
            item : items._items[0] ,
            position : {
                left:0,
                top:0
            },
            show : false
        };
        
        $scope.gridview = true;

        $scope.open = function(path) {
            $location.path(path);
        };

        $scope.edit = function(item) {
            $scope.editItem = item;
        };

        $scope.closeEdit = function() {
            $scope.editItem = null;
        };

        

        
    }];
});
