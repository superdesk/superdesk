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

    DeskDropdownDirective.$inject = ['desks', '$route', 'preferencesService', '$location', 'reloadService'];
    function DeskDropdownDirective(desks, $route, preferencesService, $location, reloadService) {
        return {
            templateUrl: 'scripts/superdesk-dashboard/views/desk-dropdown.html',
            link: function(scope) {

                scope.select = function selectDesk(desk) {
                    scope.selected = desk;
                    desks.setCurrentDeskId(desk._id);

                    if (desk._id === 'personal') {
                        $location.path('/workspace/content');
                    }
                };

                desks.initialize().then(function() {
                    desks.fetchCurrentUserDesks().then(function(userDesks) {
                        scope.userDesks = userDesks._items;
                        scope.selected = desks.getCurrentDesk();
                    });
                });
            }
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

    .service('workspace', require('./workspace-service'))
    .directive('sdWidget', require('./sd-widget-directive'))
    .directive('sdDeskDropdown', DeskDropdownDirective)

    .filter('wcodeFilter', function() {
        return function(input, values) {
            return _.pick(input, _.difference(_.keys(input), _.keys(values)));
        };
    })

    .config(['superdeskProvider', function(superdesk) {
        superdesk.activity('/workspace', {
            label: gettext('Workspace'),
            description: gettext('Customize your widgets and views'),
            controller: require('./workspace-controller'),
            templateUrl: 'scripts/superdesk-dashboard/views/workspace.html',
            topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
            priority: -1000,
            category: superdesk.MENU_MAIN
        });
    }]);
});
