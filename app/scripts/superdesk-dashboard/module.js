define([
    'angular',
    './controllers/main',
    './services',
    './directives',
    './filters',
    './widgets/worldClock/worldClock'
], function(angular) {
    'use strict';

    angular.module('superdesk.dashboard', [
        'superdesk.dashboard.services',
        'superdesk.dashboard.directives',
        'superdesk.dashboard.filters',
        'superdesk.widgets.worldClock'
    ])
    .constant('widgetsPath', 'scripts/superdesk-dashboard/widgets/')
    .config(['activityProvider', function(activityProvider) {
        activityProvider.activity('dashboard', {
            href: '/',
            label: '',
            menuLabel: gettext('Dashboard'),
            controller: require('superdesk-dashboard/controllers/main'),
            templateUrl: 'scripts/superdesk-dashboard/views/main.html',
            resolve: {},
            priority: -1000
        });
    }]);
});
