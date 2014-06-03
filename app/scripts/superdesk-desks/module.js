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

    app
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/desks/', {
                    label: gettext('Desks'),
                    templateUrl: require.toUrl('./views/main.html'),
                    controller: require('./controllers/main'),
                    category: superdesk.MENU_MAIN,
                    beta: true
                })

                .activity('/settings/desks', {
                    label: gettext('Desks'),
                    controller: require('./controllers/settings'),
                    templateUrl: require.toUrl('./views/settings.html'),
                    category: superdesk.MENU_SETTINGS,
                    priority: -800,
                    beta: true
                });
        }])
        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('desks', {
                type: 'http',
                backend: {
                    rel: 'desks'
                }
            });
            apiProvider.api('users', {
                type: 'http',
                backend: {rel: 'users'}
            });
        }]);

    return app;
});
