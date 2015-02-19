define(['lodash'], function(_) {
    'use strict';

    WorkspaceController.$inject = ['$scope', 'widgets', 'workspace', 'ItemList'];
    function WorkspaceController($scope, widgets, workspace, ItemList) {

        $scope.flags = $scope.flags || {};
        $scope.flags.loading = true;
        $scope.flags.edit = false;

        $scope.selectedWidget = null;

        $scope.selectWidget = function(widget) {
            $scope.selectedWidget = widget || null;
        };

        workspace.load(widgets).then(function() {
            $scope.userWidgets = workspace.widgets;
            updateAvailableWidgets();
            $scope.flags.loading = false;
        });

        function updateAvailableWidgets() {
            var userWidgetWcodes = _.indexBy($scope.userWidgets, '_id');
            $scope.availableWidgets = _.filter(widgets, function(widget) {
                return !userWidgetWcodes[widget._id] || widget.multiple;
            });
        }

        function saveUserWidgets() {
            $scope.flags.loading = true;
            workspace.save().then(function() {
                updateAvailableWidgets();
                $scope.flags.loading = false;
            });
        }

        $scope.addWidget = function(widget) {
            var newWidget = angular.extend({}, widget, {row: 1, col: 1});
            $scope.userWidgets.push(newWidget);
            $scope.selectWidget();
            saveUserWidgets();
        };

        $scope.saveWidgets = function() {
            $scope.flags.edit = false;
            saveUserWidgets();
        };
    }

    return WorkspaceController;
});
