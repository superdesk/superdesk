define([
    'angular',
    './controllers/main'
], function(angular) {
    'use strict';

    angular.module('superdesk.settings', [])
        .config(function(activityProvider) {
            activityProvider.activity('settings', {
                href: '/settings/:tab?',
                menuHref: '/settings/',
                label: gettext('Settings'),
                priority: 0,
                controller: require('superdesk-settings/controllers/main'),
                templateUrl: 'scripts/superdesk-settings/views/main.html',
                resolve: {
                    tab: ['$route', function($route) {
                        return $route.current.params.tab || null;
                    }]
                }
            });
        });
});
