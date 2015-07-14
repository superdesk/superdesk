define([
    'angular',
    'require',
    './workspace-controller',
    './workspace-service',
    './sd-widget-directive',
    './widgets-provider',
    './grid/grid',
    './world-clock/world-clock'
], function(angular, require) {
    'use strict';

    DashboardController.$inject = ['$scope', 'desks', 'widgets', 'api', 'session'];
    function DashboardController($scope, desks, widgets, api, session) {
        var vm = this;

        desks.initialize().then(function() {
            $scope.$watch(getActiveDesk, setupWorkspace);
        });

        function getActiveDesk() {
            return desks.active.desk;
        }

        function setupWorkspace(desk) {
            var criteria = {};
            if (desk && !desks.isPersonal(desk)) {
                criteria.desk = desk;
            } else {
                criteria.user = session.identity._id;
            }

            vm.current = null;
            api.query('workspaces', {where: criteria})
                .then(function(workspaces) {
                    if (workspaces._items.length) {
                        startEdit(workspaces._items[0]);
                    } else {
                        // BC: use existing user workspace if present in user profile
                        startEdit({widgets: criteria.user && session.identity.workspace ? session.identity.workspace.widgets : []});
                        angular.extend(vm.current, criteria);
                    }

                    vm.availableWidgets = getAvailableWidgets(vm.widgets);
                });
        }

        function getAvailableWidgets(userWidgets) {
            return _.filter(widgets, function(widget) {
                return widget.multi || _.find(userWidgets, {_id: widget._id}) == null;
            });
        }

        this.addWidget = function(widget) {
            this.widgets.push(widget);
            this.availableWidgets = getAvailableWidgets(this.widgets);
            this.selectWidget();
            this.save();
        };

        this.selectWidget = function(widget) {
            this.selectedWidget = widget || null;
        };

        function startEdit(workspace) {
            vm.current = workspace;
            vm.widgets = extendWidgets(workspace.widgets || []);
        }

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
        'superdesk.legal_archive'
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
            priority: -1000,
            category: superdesk.MENU_MAIN,
            reloadOnSearch: true
        });
    }]);
});
