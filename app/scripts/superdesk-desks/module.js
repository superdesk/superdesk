define([
    'jquery',
    'angular',
    'angular-ui',
    'superdesk/server',
    './resources',
    './controllers/main',
    './controllers/settings',
    './directives',
], function($, angular) {
    'use strict';

    angular.module('superdesk.desks', [
        'superdesk.desks.resources',
        'superdesk.desks.directives'
    ])
    .controller('DesksSettingsCtrl', require('superdesk-desks/controllers/settings'))

    .config(function(activityProvider) {
        activityProvider
            .activity('desks', {
                permissions: {
                    label: 'View desks',
                    requires: {}
                },
                href: '/desks/',
                menuHref: '/desks/',
                label: gettext('Desks'),
                templateUrl: 'scripts/superdesk-desks/views/main.html',
                controller: require('superdesk-desks/controllers/main')
            });
    })
    .config(function(settingsProvider) {
        settingsProvider.register('desks', {
            label: gettext('Desks'),
            templateUrl: 'scripts/superdesk-desks/views/settings.html'
        });
    });

});
