define(['angular'], function(angular){
    'use strict';

    return ['$scope', 'generalSettings', 'tab', 
    function($scope, generalSettings, tab){
        $scope.selected = null;
        $scope.generalSettings = generalSettings;
        
        if (tab && generalSettings[tab]) {
            $scope.selected = generalSettings[tab];
        }
    }];
});