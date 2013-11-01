define([
    'angular',
    './controllers/main'
], function(angular) {
    'use strict';

    angular.module('superdesk.settings', [])
        .config(function($routeProvider) {
            $routeProvider
                .when('/settings/:tab?', {
                    controller: require('superdesk/settings/controllers/main'),
                    templateUrl: 'scripts/superdesk/settings/views/main.html',
                    resolve: {
                        tab: ['$route', function($route) {
                            return $route.current.params.tab || null;
                        }]
                    }
                })
                // temporary fake route, just to have menu fixed
                .when('/settings', {
                    menu: {
                        label: gettext('Settings'),
                        priority: 0
                    }
                });
        });

});
