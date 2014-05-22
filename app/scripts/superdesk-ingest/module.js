define([
    'angular',
    'require',
    './controllers/list',
    './controllers/settings',
    './ingest-widget/ingest'
], function(angular, require) {
    'use strict';

    var app = angular.module('superdesk.ingest', ['superdesk.widgets.ingest']);

    app.config(['superdeskProvider', function(superdesk) {
        superdesk
            .activity('/ingest/', {
                label: gettext('Ingest'),
                priority: 100,
                controller: require('./controllers/list'),
                templateUrl: require.toUrl('../superdesk-archive/views/list.html'),
                category: superdesk.MENU_MAIN,
                reloadOnSearch: false
            })
            .activity('/settings/ingest', {
                label: gettext('Ingest Feed'),
                templateUrl: require.toUrl('./views/settings/settings.html'),
                controller: require('./controllers/settings'),
                category: superdesk.MENU_SETTINGS
            });
    }]);

    app.config(['apiProvider', function(apiProvider) {
        apiProvider.api('ingest', {
            type: 'http',
            backend: {
                rel: 'ingest'
            }
        });
    }]);

    return app;
});
