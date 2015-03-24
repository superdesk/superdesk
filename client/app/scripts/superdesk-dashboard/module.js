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

                scope.select = function selectDesk(desk, reloadRoute) {
                    if (angular.isUndefined(reloadRoute)) {
                        reloadRoute = true;
                    }

                    desks.setCurrentDesk(desk);
                    scope.selected = desk;

                    if (desk._id === 'personal' && $location.path() === '/workspace/ingest') {
                       $location.path('/workspace/content') ;
                    }

                    if (reloadRoute) {
                        $route.reload();
                    }
                };

                desks.initialize()
                .then(function() {
                    desks.fetchCurrentUserDesks().then(function (userDesks) {
                    	scope.userDesks = userDesks._items;
                    	if (!desks.activeDeskId && scope.userDesks.length) {
                    		scope.select(scope.userDesks[0], false);
                    	} else if (desks.getCurrentDesk() != null) {
                    		scope.select(desks.getCurrentDesk(), false);
                    	}
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
        'superdesk.itemList'
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
            templateUrl: require.toUrl('./views/workspace.html'),
            topTemplateUrl: require.toUrl('./views/workspace-topnav.html'),
            priority: -1000,
            category: superdesk.MENU_MAIN
        });
    }]);
});
