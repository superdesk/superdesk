define([
    'angular',
    'require',
    './controllers/list',
    './controllers/upload',
    './directives'
], function(angular, require) {
    'use strict';

    var app = angular.module('superdesk.archive', [
        require('./directives').name
    ]);

    app.config(['superdeskProvider', function(superdesk) {
        superdesk
            .activity('/archive/', {
                label: gettext('Archive'),
                priority: 100,
                controller: require('./controllers/list'),
                templateUrl: require.toUrl('./views/list.html'),
                category: superdesk.MENU_MAIN,
                reloadOnSearch: false
            })
            .activity('upload.media', {
                label: gettext('Upload media'),
                modal: true,
                cssClass: 'upload-media responsive-popup',
                controller: require('./controllers/upload'),
                templateUrl: require.toUrl('./views/upload.html'),
                filters: [
                    {action: 'upload', type: 'media'}
                ]
            });
    }]);

    app.config(['apiProvider', function(apiProvider) {
        apiProvider.api('archive', {
            type: 'http',
            backend: {
                rel: 'ingest'
            }
        });
    }]);

    return app;
});
