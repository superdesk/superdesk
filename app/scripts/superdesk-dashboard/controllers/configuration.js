define(['angular'], function(angular){
    'use strict';

    return ['$scope','$modalInstance', 'widgetService', 'widget',
    function ($scope, $modalInstance, widgetService, widget) {
        $scope.widget = widget;
        $scope.configuration = _.cloneDeep($scope.widget.configuration);

        $scope.closeModal = function() {
            $modalInstance.close();
        };

        $scope.save = function() {
            widgetService.saveConfiguration(widget.wcode, $scope.configuration);
            $scope.widget.configuration = $scope.configuration;
        };
    }];
});