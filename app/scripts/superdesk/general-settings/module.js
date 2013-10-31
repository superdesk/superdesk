define([
    'angular',
    'bootstrap_ui',
    './directives',
    './controllers/main'
], function(angular) {
    'use strict';

    angular.module('superdesk.generalSettings', [
        'superdesk.generalSettings.directives',
        'superdesk.directives',
        'ui.bootstrap'
    ])
        .config(function($routeProvider) {
            $routeProvider
                .when('/settings/:tab?', {
                    controller: require('superdesk/general-settings/controllers/main'),
                    templateUrl: 'scripts/superdesk/general-settings/views/main.html',
                    resolve: {
                        tab: ['$route', function($route) {
                            if ($route.current.params.tab) {
                                return $route.current.params.tab;
                            } else {
                                return undefined;
                            }
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
