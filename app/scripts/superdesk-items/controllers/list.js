define(['lodash', 'angular'], function(_, angular) {
    'use strict';

    return ['$scope', '$routeParams', 'items', 'providerRepository',
    function($scope, $routeParams, items, providerRepository) {

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
        
        $scope.gridview = true;

        $scope.edit = function(item) {
            $scope.editItem = item;
        };

        $scope.closeEdit = function() {
            $scope.editItem = null;
        };
    }];
});
