define([
    'angular',
    './controllers/main'
], function(angular) {
    'use strict';

    angular.module('superdesk.settings', [])
        .config(function(menuProvider) {
            menuProvider.menu('settings', {
                label: gettext('Settings'),
                href: '/settings',
                priority: 0
            });
        })
        .config(function($routeProvider) {
            $routeProvider
                .when('/settings/:tab?', {
                    controller: require('superdesk-settings/controllers/main'),
                    templateUrl: 'scripts/superdesk-settings/views/main.html',
                    resolve: {
                        tab: ['$route', function($route) {
                            return $route.current.params.tab || null;
                        }]
                    },
                    label: gettext('Settings')
                });
        });

});
