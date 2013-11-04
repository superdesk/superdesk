define(['angular'], function(angular){
    'use strict';

    return ['$scope', 'settings', 'locationParams', 'tab',
    function($scope, settings, locationParams, tab) {
        $scope.selected = null;
        $scope.settings = settings;
        
        if (tab) {
            if (settings[tab]) {
                $scope.selected = settings[tab];
            } else {
                locationParams.path('/settings');
            }
        }
    }];
});