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

    DeskDropdownDirective.$inject = ['desks', '$route', 'preferencesService', '$location'];
    function DeskDropdownDirective(desks, $route, preferencesService, $location) {
        return {
            templateUrl: 'scripts/superdesk-dashboard/views/desk-dropdown.html',
            link: function(scope) {

                scope.select = function selectDesk(desk) {
                    scope.selected = desk;
                    desks.setCurrentDesk(desk._id === 'personal' ? null : desk);
                    $location.search('_id', null);
                    $location.search('desk', desks.activeDeskId);
                    $location.path('/workspace');
                };

                desks.fetchCurrentUserDesks()
                    .then(function(userDesks) {
                        scope.userDesks = userDesks._items;
                        scope.selected = _.find(scope.userDesks, {_id: desks.activeDeskId}) || null;
                    });
            }
        };
    }

    DashboardController.$inject = ['$location', 'widgets', 'api', 'session'];
    function DashboardController($location, widgets, api, session) {
        var criteria = {},
            search = $location.search();

        if (search.desk) {
            criteria.desk = search.desk;
        } else {
            criteria.user = session.identity._id;
        }

        function getAvailableWidgets(userWidgets) {
            return _.filter(widgets, function(widget) {
                return widget.multi || _.find(userWidgets, {_id: widget._id}) == null;
            });
        }

        api.query('dashboards', {where: criteria})
        .then(angular.bind(this, function(dashboards) {
            if (dashboards._items.length) {
                startEdit(dashboards._items[0]);
            } else {
                startEdit({widgets: criteria.user && session.identity.workspace ? session.identity.workspace.widgets : []}); // bc
                angular.extend(this.current, criteria);
            }

            this.availableWidgets = getAvailableWidgets(this.widgets);
        }));

        this.addWidget = function(widget) {
            this.widgets.push(widget);
            this.availableWidgets = getAvailableWidgets(this.widgets);
            this.selectWidget();
            this.save();
        };

        this.selectWidget = function(widget) {
            this.selectedWidget = widget || null;
        };

        var startEdit = angular.bind(this, function(dashboard) {
            this.current = dashboard;
            this.widgets = extendWidgets(dashboard.widgets || []);
        });

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
            api.save('dashboards', this.current, diff);
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
        'superdesk.itemList'
    ])

    .directive('sdWidget', require('./sd-widget-directive'))
    .directive('sdDeskDropdown', DeskDropdownDirective)
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
