define(['lodash'], function(_) {
    'use strict';

    return ['$scope','$modalInstance', 'widgetService', 'widget', 'id',
    function ($scope, $modalInstance, widgetService, widget, id) {
        $scope.widget = widget;
        $scope.id = id;
        $scope.configuration = _.cloneDeep($scope.widget.configuration);

        $scope.closeModal = function() {
            $modalInstance.close();
        };

        $scope.save = function() {
            widgetService.saveConfiguration($scope.id, $scope.configuration);
            $scope.widget.configuration = $scope.configuration;
        };
    }];
});