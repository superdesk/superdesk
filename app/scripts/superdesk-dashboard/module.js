define([
    'angular',
    'require',
    './controllers/main',
    './services',
    './directives',
    './filters',
    './widgets/worldClock/worldClock'
], function(angular, require) {
    'use strict';

    angular.module('superdesk.dashboard', [
        'superdesk.dashboard.services',
        'superdesk.dashboard.directives',
        'superdesk.dashboard.filters',
        'superdesk.widgets.worldClock'
    ])
    .constant('widgetsPath', 'scripts/superdesk-dashboard/widgets/')
    .config(['superdeskProvider', function(superdesk) {
        superdesk.activity('/dashboard', {
            label: gettext('Dashboard'),
            controller: require('./controllers/main'),
            templateUrl: 'scripts/superdesk-dashboard/views/main.html',
            priority: -1000,
            category: superdesk.MENU_MAIN
        });
    }]);
});
