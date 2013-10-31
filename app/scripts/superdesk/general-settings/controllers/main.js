define(['angular'], function(angular){
    'use strict';

    return ['$scope', 'generalSettings', 'locationParams', 'tab',
    function($scope, generalSettings, locationParams, tab){
        $scope.selected = null;
        $scope.generalSettings = generalSettings;
        
        if (tab) {
            if (generalSettings[tab]) {
                $scope.selected = generalSettings[tab];
            } else {
                locationParams.path('/settings');
            }
        }
    }];
});