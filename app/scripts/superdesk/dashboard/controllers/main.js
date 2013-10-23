define(['angular'], function(){
    'use strict';

    return ['$scope', 'widgetService', 'widgetList', 'widgets',
        function($scope, widgetService, widgetList, widgets){

            $scope.initialize = function() {
                $scope.widgetList = widgetList;
                $scope.widgets = widgets;
                $scope.widgetBoxStatus = false;
                $scope.editMode = false;
            };

            $scope.saveWidgets = function() {
                widgetService.saveWidgets($scope.widgets);
                $scope.editMode = false;
            };

            $scope.initialize();

        }];
});
