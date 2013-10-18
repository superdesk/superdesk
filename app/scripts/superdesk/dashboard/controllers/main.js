define(['angular'], function(){
    'use strict';

    return ['$scope', 'widgetList', '$timeout',
        function($scope, widgetList, $timeout){ 

            $scope.availableWidgets = [];
            $scope.allWidgets = [];

            widgetList.get(function(data){
                $scope.allWidgets = data.allWidgets;
                $scope.widgets = data.userWidgets;
            });

            var getAvailableWidgets = function() {
                var allCodes = [];
                var selectedCodes = [];
                angular.forEach($scope.allWidgets, function(value,key){
                    allCodes.push(value.wcode);
                });
                angular.forEach($scope.widgets, function(value,key){
                    selectedCodes.push(value.wcode);
                });
                $scope.availableWidgets = _.difference(allCodes, selectedCodes);

            }

            $scope.addWidget = function(widget) {
                $scope.widgets.push(widget);
            };

            $scope.showWidgetBox = false;
            $scope.widgetBoxList = true;

            $scope.openWidgetBox = function() {
                getAvailableWidgets();
                $scope.showWidgetBox = true;
                $scope.widgetBoxList = true;
            }


            $scope.editmode = false;

            $scope.disableDragging = function() {
                $scope.gridster.disable();
                $scope.editmode = false;
            };

            $scope.enableDragging = function() {
                $scope.gridster.enable();
                $scope.editmode = true;
            };


        }];
});
