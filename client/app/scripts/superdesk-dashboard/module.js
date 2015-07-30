define([
    'angular',
    'require',
    './sd-widget-directive',
    './widgets-provider',
    './grid/grid',
    './world-clock/world-clock'
], function(angular, require) {
    'use strict';

    DashboardController.$inject = ['$scope', 'desks', 'widgets', 'api', 'session', 'workspaces'];
    function DashboardController($scope, desks, widgets, api, session, workspaces) {
        var vm = this;

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

        function getAvailableWidgets(userWidgets) {
            return _.filter(widgets, function(widget) {
                return widget.multi || _.find(userWidgets, {_id: widget._id}) == null;
            });
        }

        this.addWidget = function(widget) {
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
            return !_.find(getAvailableWidgets(this.widgets), widget);
        };

        function extendWidgets(currentWidgets) {
            return _.map(currentWidgets, function(widget) {
                var original = _.find(widgets, {_id: widget._id});
                return angular.extend({}, original, widget);
            });
        }

        function pickWidgets(widgets) {
            return _.map(widgets, function(widget) {
                return _.pick(widget, ['_id', 'configuration', 'sizex', 'sizey', 'col', 'row']);
            });
        }

        this.save = function() {
            this.edit = false;
            var diff = angular.extend({}, this.current);
            diff.widgets = pickWidgets(this.widgets);
            api.save('workspaces', this.current, diff);
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
        'superdesk.workspace.content',
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
            sideTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-sidenav.html',
            priority: -1000,
            category: superdesk.MENU_MAIN,
            reloadOnSearch: true
        });
    }]);
});
