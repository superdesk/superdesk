define(['angular'], function(angular){
    'use strict';

    return ['$scope','$modalInstance', 'widgetService', 'widget', 'controller', 'template', 'configuration',
    function ($scope, $modalInstance, widgetService, widget, controller, template, configuration) {
        $scope.controller = controller;
        $scope.template = template;
        $scope.configuration = configuration;
        $scope.widget = widget;

        $scope.closeModal = function() {
            $modalInstance.dismiss('cancel');
        };

        $scope.save = function() {
            widgetService.saveConfiguration(widget.wcode, $scope.configuration);
        };
    }];
});