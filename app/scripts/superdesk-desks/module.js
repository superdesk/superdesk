define([
    'angular',
    'require',
    'view',
    './resources',
    './controllers/main',
    './controllers/settings',
    './directives'
], function(angular, require, view) {
    'use strict';

    var app = angular.module('superdesk.desks', [
        'superdesk.desks.resources',
        'superdesk.desks.directives'
    ]);

    app.config(['superdeskProvider', function(superdesk) {
        superdesk
            .activity('/desks', {
                label: gettext('Desks'),
                templateUrl: view('main.html', app),
                controller: require('./controllers/main'),
                category: superdesk.MENU_MAIN
            })

            .activity('/settings/desks', {
                label: gettext('Desks'),
                controller: require('./controllers/settings'),
                templateUrl: view('settings.html', app),
                category: superdesk.MENU_SETTINGS,
                priority: -800
            });
    }]);
});
