define([
    'angular',
    'require',
    './resources',
    './controllers/main',
    './controllers/settings',
    './directives'
], function(angular, require) {
    'use strict';

    var app = angular.module('superdesk.desks', [
        'superdesk.desks.resources',
        'superdesk.desks.directives'
    ]);

    app.controller('DesksSettingsCtrl', require('./controllers/settings'));

    app.config(['superdeskProvider', function(superdesk) {
        superdesk.activity('desks', {
            when: '/desks/',
            href: '/desks/',
            label: gettext('Desks'),
            templateUrl: 'scripts/superdesk-desks/views/main.html',
            controller: require('./controllers/main'),
            category: superdesk.MENU_MAIN
        });
    }]);

    app.config(['settingsProvider', function(settingsProvider) {
        settingsProvider.register('desks', {
            label: gettext('Desks'),
            templateUrl: 'scripts/superdesk-desks/views/settings.html'
        });
    }]);
});
