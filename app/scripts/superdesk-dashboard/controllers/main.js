define(['angular'], function(){
    'use strict';

    return ['$scope', 'widgets', 'widgetService',
        function($scope, widgets, widgetService){

            $scope.userWidgets = widgetService.load();
            $scope.editStatus = false;
            $scope.widgetBoxStatus = false;
            $scope.selectedWidget = null;

            function updateAvailable() {
                var keys = _.keys($scope.userWidgets);
                $scope.hasWidgets = keys.length;
                $scope.availableWidgets = _.omit(widgets, keys);
            }

            function save() {
                widgetService.save($scope.userWidgets);
                updateAvailable();
            }

            $scope.addWidget = function(widget) {
                angular.extend(widget, {row: 1, col: 1});
                $scope.userWidgets[widget.wcode] = widget;
                save();
            };

            $scope.saveWidgets = function() {
                $scope.editStatus = false;
                save();
            };

            updateAvailable();
        }];
});
