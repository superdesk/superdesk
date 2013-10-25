define(['angular'], function(){
    'use strict';

    return ['$scope', 'widgets', 'widgetService',
        function($scope, widgets, widgetService){

            $scope.initialize = function() {
                $scope.widgetList = widgets;
                $scope.widgets = widgetService.load();
                $scope.numWidgets = _.keys($scope.widgets).length;

                $scope.editStatus = false;
                $scope.widgetBoxStatus = false;
                $scope.selectedWidget = null;
            };

            $scope.addWidget = function(wcode) {
                var widget = {
                    sizex: $scope.widgetList[wcode].sizex,
                    sizey: $scope.widgetList[wcode].sizey,
                    row: 1,
                    col: 1
                };
                $scope.widgets[wcode] = widget;
                widgetService.save($scope.widgets);
            };

            $scope.saveWidgets = function() {
                widgetService.save($scope.widgets);
                $scope.editStatus = false;
            };

            $scope.initialize();

        }];
});
