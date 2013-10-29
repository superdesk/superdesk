define([
    'angular',
    'angular-route',
    'gridster',
    './controllers/main',
    './providers',
    './services',
    './directives',
    './filters',
    './widgets/worldclock'
], function(angular) {
    'use strict';

    angular.module('superdesk.dashboard', [
        'ngRoute',
        'superdesk.dashboard.providers',
        'superdesk.dashboard.services',
        'superdesk.dashboard.directives',
        'superdesk.dashboard.filters',
        'superdesk.dashboard.widgets.worldclock'
    ])
    .config(['widgetsProvider', function(widgetsProvider) {
        widgetsProvider
            .widget('weather', {
                name: 'Weather',
                class: 'default',
                icon: 'leaf',
                max_sizex: 2,
                max_sizey: 2,
                sizex: 1,
                sizey: 2,
                thumbnail: 'images/sample/widgets/weather.png',
                template: 'scripts/superdesk/dashboard/views/widgets/widget-default.html',
                description: 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'
            })
            .widget('worldClock', {
                name: 'World Clock',
                class: 'world-clock',
                icon: 'time',
                max_sizex: 2,
                max_sizey: 1,
                sizex: 1,
                sizey: 1,
                thumbnail: 'images/sample/widgets/worldclock.png',
                template: 'scripts/superdesk/dashboard/views/widgets/widget-worldclock.html',
                description: 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'
            })
            .widget('widgetCool', {
                name: 'Widget Cool',
                class: 'default',
                icon: 'leaf',
                max_sizex: 2,
                max_sizey: 2,
                sizex: 2,
                sizey: 1,
                thumbnail: 'images/sample/widgets/default.png',
                template: 'scripts/superdesk/dashboard/views/widgets/widget-default.html',
                description: 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'
            })
            .widget('dashDash', {
                name: 'DashDash',
                class: 'default',
                icon: 'leaf',
                max_sizex: 2,
                max_sizey: 2,
                sizex: 1,
                sizey: 1,
                thumbnail: 'images/sample/widgets/default.png',
                template: 'scripts/superdesk/dashboard/views/widgets/widget-default.html',
                description: 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'
            });
    }])
    .config(['$routeProvider', function($routeProvider) {
        $routeProvider
            .when('/', {
                controller: require('superdesk/dashboard/controllers/main'),
                templateUrl: 'scripts/superdesk/dashboard/views/main.html',
                resolve: {},
                menu: {
                    label: 'Dashboard',
                    priority: 0
                }
            });
    }]);
});
