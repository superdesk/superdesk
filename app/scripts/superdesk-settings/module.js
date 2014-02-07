define([
    'angular',
    'lodash'
], function(angular, _) {
    'use strict';

    angular.module('superdesk.settings', [])
        .config(['superdeskProvider', function(superdesk) {
            superdesk.activity('/settings', {
                label: gettext('Settings'),
                controller: function() {},
                templateUrl: 'scripts/superdesk-settings/views/main.html',
                category: superdesk.MENU_MAIN,
                priority: 1000
            });
        }])
        .directive('sdSettingsView', ['$route', 'superdesk', function($route, superdesk) {
            return {
                scope: {},
                transclude: true,
                templateUrl: 'scripts/superdesk-settings/views/settings-view.html',
                link: function(scope, elem, attrs) {
                    scope.settings = _.values(_.where(superdesk.activities, {category: superdesk.MENU_SETTINGS}));
                    scope.currentRoute = $route.current;
                }
            };
        }]);
});
