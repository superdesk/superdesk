define(['lodash', 'angular'], function(_, angular) {
    'use strict';

    return ['$scope', '$routeParams', 'items', 'providerRepository', 'storage',
    function($scope, $routeParams, items, providerRepository, storage) {

        $scope.items = items;

        providerRepository.findAll().then(function(providers) {
            $scope.providers = providers;
            if ('provider' in $routeParams) {
                $scope.activeProvider = _.find(providers._items, {_id: $routeParams.provider});
            }
        });

        $scope.selectedItem = {
            item : items._items[0] ,
            position : {
                left:0,
                top:0
            },
            show : false
        };
        

        var userCompact = storage.getItem('archive-compact');
        $scope.compactList = (userCompact === null) ? false : userCompact;
        
        $scope.toggleCompact = function() {
            $scope.compactList = ! $scope.compactList;
            storage.setItem('archive-compact', $scope.compactList, true);
        };


        var userView = storage.getItem('archive-view');
        $scope.gridview = (userView === null) ? true : userView;
        
        $scope.toggleView = function(val) {
            $scope.gridview = val;
            storage.setItem('archive-view', val, true);
        };

        

        $scope.edit = function(item) {
            $scope.editItem = item;
        };

        $scope.closeEdit = function() {
            $scope.editItem = null;
        };
    }];
});
