define([
    'angular',
    'angular-route',
    'gridster',
    './controllers/main',
    './services',
    './directives',
    './filters',
    './widgets/worldClock/worldClock'
], function(angular) {
    'use strict';

    angular.module('superdesk.dashboard', [
        'ngRoute',
        'superdesk.userSettings',
        'superdesk.dashboard.services',
        'superdesk.dashboard.directives',
        'superdesk.dashboard.filters',
        'superdesk.widgets.worldClock'
    ])
    .constant('widgetsPath', 'scripts/superdesk-dashboard/widgets/')
    .config(['widgetsProvider', function(widgetsProvider) {
        widgetsProvider
            .widget('weather', {
                name: 'Weather',
                multiple: true,
                class: 'default',
                icon: 'leaf',
                max_sizex: 2,
                max_sizey: 2,
                sizex: 1,
                sizey: 2,
                thumbnail: 'images/sample/widgets/weather.png',
                template: 'scripts/superdesk-dashboard/views/widgets/widget-default.html',
                configuration: {},
                description: 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'
            })
            .widget('widgetCool', {
                name: 'Widget Cool',
                multiple: true,
                class: 'default',
                icon: 'leaf',
                max_sizex: 2,
                max_sizey: 2,
                sizex: 2,
                sizey: 1,
                thumbnail: 'images/sample/widgets/default.png',
                template: 'scripts/superdesk-dashboard/views/widgets/widget-default.html',
                configuration: {},
                description: 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'
            })
            .widget('dashDash', {
                name: 'DashDash',
                multiple: true,
                class: 'default',
                icon: 'leaf',
                max_sizex: 2,
                max_sizey: 2,
                sizex: 1,
                sizey: 1,
                thumbnail: 'images/sample/widgets/default.png',
                template: 'scripts/superdesk-dashboard/views/widgets/widget-default.html',
                configuration: {},
                description: 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'
            });
    }])
    .config(['$routeProvider', function($routeProvider) {
        $routeProvider
            .when('/', {
                controller: require('superdesk-dashboard/controllers/main'),
                templateUrl: 'scripts/superdesk-dashboard/views/main.html',
                resolve: {},
                menu: {
                    label: 'Dashboard',
                    priority: -1000
                }
            });
    }]);
});
