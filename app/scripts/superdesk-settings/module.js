define([
    'angular',
    'require',
    './controllers/main'
], function(angular, require) {
    'use strict';

    angular.module('superdesk.settings', [])
        .config(['superdeskProvider', function(superdesk) {
            superdesk.activity('settings', {
                when: '/settings/:tab?',
                href: '/settings/',
                label: gettext('Settings'),
                controller: require('./controllers/main'),
                templateUrl: 'scripts/superdesk-settings/views/main.html',
                resolve: {
                    tab: ['$route', function($route) {
                        return $route.current.params.tab || null;
                    }]
                },
                category: superdesk.MENU_MAIN,
                priority: 1000
            });
        }]);
});
