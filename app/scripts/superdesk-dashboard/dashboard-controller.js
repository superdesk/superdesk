define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'superdesk', 'widgetService',
        function($scope, superdesk, widgetService) {

            $scope.userWidgets = widgetService.load();
            $scope.editStatus = false;
            $scope.widgetBoxStatus = false;
            $scope.selectedWidget = null;

            function updateAvailable() {
                var wcodeList = _.uniq(_.pluck($scope.userWidgets, 'wcode'));

                var keys = _.keys($scope.userWidgets);
                $scope.hasWidgets = keys.length;

                var omitList = [];
                _.forEach(superdesk.widgets, function(widget) {
                    if (!widget.multiple && _.indexOf(wcodeList, widget.wcode) > -1) {
                        omitList.push(widget.wcode);
                    }
                });

                $scope.availableWidgets = _.omit(superdesk.widgets, omitList);
            }

            function save() {
                widgetService.save($scope.userWidgets);
                updateAvailable();
            }

            $scope.addWidget = function(widget) {
                var newWidget = angular.extend({}, widget, {row: 1, col: 1});

                var ids = _.keys($scope.userWidgets);
                var lastId = _.max(ids);
                if (lastId < 0) {
                    lastId = 0;
                }
                lastId = parseInt(lastId, 10);
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
