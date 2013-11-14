define(['angular'], function(){
    'use strict';

    return ['$scope', 'widgets', 'widgetService',
        function($scope, widgets, widgetService){

            $scope.userWidgets = widgetService.load();
            $scope.editStatus = false;
            $scope.widgetBoxStatus = false;
            $scope.selectedWidget = null;

            function updateAvailable() {
                var wcodeList = _.uniq(_.pluck($scope.userWidgets, 'wcode'));

                var keys = _.keys($scope.userWidgets);
                $scope.hasWidgets = keys.length;

                var omitList = [];
                _.forEach(widgets, function(widget) {
                    if (!widget.multiple && _.indexOf(wcodeList, widget.wcode) > -1) {
                        omitList.push(widget.wcode);
                    }
                });

                $scope.availableWidgets = _.omit(widgets, omitList);
            }

            function save() {
                widgetService.save($scope.userWidgets);
                updateAvailable();
            }

            $scope.addWidget = function(widget) {
                var newWidget = angular.extend({}, widget, {row: 1, col: 1});
                var lastId = 0;
                _.forEach($scope.userWidgets, function(newWidget, id) {
                    id = parseInt(id, 10);
                    if (id > lastId) {
                        lastId = id;
                    }
                });
                $scope.userWidgets[lastId + 1] = newWidget;
                save();
            };

            $scope.saveWidgets = function() {
                $scope.editStatus = false;
                save();
            };

            updateAvailable();
        }];
});
