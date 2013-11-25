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
    .config(function(activityProvider) {
        activityProvider.activity('dashboard', {
            href: '/',
            label: gettext('Dashboard'),
            controller: require('superdesk-dashboard/controllers/main'),
            templateUrl: 'scripts/superdesk-dashboard/views/main.html',
            resolve: {},
            priority: -1000
        });
    });
});
