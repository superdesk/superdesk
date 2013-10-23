define([
    'angular',
    'angular-route',
    'gridster',
    './controllers/main',
    './directives',
    './filters',
    './resources',
    './services',
    './widgets/worldclock'
], function(angular) {
    'use strict';

    angular.module('superdesk.dashboard', [
        'ngRoute',
        'superdesk.dashboard.directives',
        'superdesk.dashboard.filters',
        'superdesk.dashboard.resources',
        'superdesk.dashboard.services',
        'superdesk.dashboard.widgets.worldclock'
    ])
    .config(['$routeProvider', function($routeProvider) {

        $routeProvider.
            when('/', {
                controller: require('superdesk/dashboard/controllers/main'),
                templateUrl: 'scripts/superdesk/dashboard/views/main.html',
                resolve: {
                    widgetList: ['widgetService', function(widgetService) {
                        return widgetService.fetchWidgetList();
                    }],
                    widgets: ['widgetService', function(widgetService) {
                        return widgetService.loadWidgets();
                    }]
                },
                menu: {
                    label: 'Dashboard',
                    priority: 0
                }
            });
    }]);
});
