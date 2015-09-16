define([
    'angular',
    'require',
    './sd-widget-directive',
    './widgets-provider',
    './grid/grid',
    './world-clock/world-clock'
], function(angular, require) {
    'use strict';

    DashboardController.$inject = ['$scope', 'desks', 'widgets', 'api', 'session', 'workspaces', 'modal', 'gettext'];
    function DashboardController($scope, desks, widgets, api, session, workspaces, modal, gettext) {
        var vm = this;

        $scope.edited = null;
        $scope.workspaces = workspaces;
        $scope.$watch('workspaces.active', setupWorkspace);
        workspaces.getActive();

        function setupWorkspace(workspace) {
            vm.current = null;
            if (workspace) {
                // do this async so that it can clean up previous grid
                $scope.$applyAsync(function() {
                    vm.current = workspace;
                    vm.widgets = extendWidgets(workspace.widgets || []);
                    vm.availableWidgets = widgets;
                });
            }
        }

        /**
         * Return the list of available widgets that can be added
         * to current dashboard
         *
         * @return {promise} list of widgets
         */
        function getAvailableWidgets(userWidgets) {
            return _.filter(widgets, function(widget) {
                return widget.multiple || _.find(userWidgets, {_id: widget._id}) == null;
            });
        }

        /**
         * Add widgets to current dashboard
         *
         * @param {object} widget
         */
        this.addWidget = function(widget) {
            if (widget.multiple) {
                widget = angular.copy(widget);
                widget.multiple_id = 0;
                angular.forEach(this.widgets, function(item) {
                    if (item._id === widget._id && item.multiple_id >= widget.multiple_id) {
                        widget.multiple_id = item.multiple_id + 1;
                    }
                });
            }
            widget.active = true;
            this.widgets.push(widget);
            this.selectWidget();
            this.save();
        };

        /*
         * If widget is not selected, opens single view of specific widget
         * @param {object} widget
         */
        this.selectWidget = function(widget) {
            if (!this.isSelected(widget)) {
                this.selectedWidget = widget || null;
            }
        };

        /*
         * Checks if widget is already selected
         * @param {object} widget
         * @returns {boolean}
         */
        this.isSelected = function (widget) {
            return widget && !_.find(getAvailableWidgets(this.widgets), widget);
        };

        function extendWidgets(currentWidgets) {
            return _.map(currentWidgets, function(widget) {
                var original = _.find(widgets, {_id: widget._id});
                return angular.extend({}, original, widget);
            });
        }

        /**
         * Prepare the widget to be saved. Filter any non-required data.
         *
         * @return {promise} widget
         */
        function pickWidgets(widgets) {
            return _.map(widgets, function(widget) {
                return _.pick(widget, ['_id', 'configuration', 'sizex', 'sizey', 'col', 'row', 'active', 'multiple_id']);
            });
        }

        /*
         * Saves current workspace
         */
        this.save = function() {
            this.edit = false;
            var diff = angular.extend({}, this.current);
            this.widgets = _.where(this.widgets, {active: true});
            diff.widgets = pickWidgets(this.widgets);
            api.save('workspaces', this.current, diff);
        };

        /*
         * Confirms and deletes current workspace
         */
        this.delete = function() {
            modal.confirm(
                gettext('Are you sure you want to delete current workspace?')
            )
            .then(function() {
                return workspaces.delete(vm.current);
            });
        };

        /*
         * Enables editing current workspace
         */
        this.rename = function() {
            $scope.edited = angular.copy(vm.current);
        };

        /*
         * Updates workspaces after editing
         */
        this.afterRename = function() {
            workspaces.getActive();
        };
    }

    // to avoid circular dependency
    angular.module('superdesk.dashboard.widgets', []).
        provider('widgets', require('./widgets-provider'));

    return angular.module('superdesk.dashboard', [
        'superdesk.activity',
        'superdesk.dashboard.widgets',
        'superdesk.dashboard.grid',
        'superdesk.dashboard.world-clock',
        'superdesk.workspace.tasks',
        'superdesk.itemList',
        'superdesk.legal_archive',
        'superdesk.workspace'
    ])

    .directive('sdWidget', require('./sd-widget-directive'))
    .controller('DashboardController', DashboardController)

    .filter('wcodeFilter', function() {
        return function(input, values) {
            return _.pick(input, _.difference(_.keys(input), _.keys(values)));
        };
    })

    .config(['superdeskProvider', function(superdesk) {
        superdesk.activity('/workspace', {
            label: gettext('Workspace'),
            description: gettext('Customize your widgets and views'),
            controller: 'DashboardController',
            controllerAs: 'dashboard',
            templateUrl: 'scripts/superdesk-dashboard/views/workspace.html',
            topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
            sideTemplateUrl: 'scripts/superdesk-workspace/views/workspace-sidenav.html',
            priority: -1000,
            adminTools: false,
            category: superdesk.MENU_MAIN
        });
    }]);
});
