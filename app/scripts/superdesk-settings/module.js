define([
    'lodash',
    'require',
    'angular'
], function(_, require, angular) {
    'use strict';

    return angular.module('superdesk.settings', [])
        .config(['superdeskProvider', function(superdesk) {
            superdesk.activity('/settings', {
                label: gettext('Settings'),
                controller: angular.noop,
                templateUrl: require.toUrl('./views/main.html'),
                category: superdesk.MENU_MAIN,
                priority: 1000
            });
        }])
        .directive('sdSettingsView', ['$route', 'superdesk', function($route, superdesk) {
            return {
                scope: {},
                transclude: true,
                templateUrl: require.toUrl('./views/settings-view.html'),
                link: function(scope, elem, attrs) {
                    superdesk.getMenu(superdesk.MENU_SETTINGS).then(function(menu) {
                        scope.settings = menu;
                    });

                    scope.currentRoute = $route.current;
                }
            };
        }]);
});
