define([
    'angular',
    'require',
    './controllers/list',
    './controllers/settings',
    './ingest-widget/ingest'
], function(angular, require) {
    'use strict';

    var app = angular.module('superdesk.ingest', ['superdesk.widgets.ingest']);

    app.value('providerTypes', {
        aap: {
            label: 'AAP',
            templateUrl: require.toUrl('./views/settings/aapConfig.html')
        },
        reuters: {
            label: 'Reuters',
            templateUrl: require.toUrl('./views/settings/reutersConfig.html')
        }
    });

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
            })
            .activity('archive', {
                label: gettext('Archive'),
                icon: 'archive',
                controller: ['$timeout', 'data', function($timeout, data) {
                    if (data.item && !data.item.archived) {
                        data.item.archiving = true;
                        $timeout(function() {
                            data.item.archiving = false;
                            data.item.archived = true;
                        }, 2000);
                    }
                }],
                filters: [
                    {action: 'archive', type: 'ingest'}
                ]
            });
    }]);

    app.config(['apiProvider', function(apiProvider) {
        apiProvider.api('ingest', {
            type: 'http',
            backend: {
                rel: 'ingest'
            }
        });
        apiProvider.api('ingestProviders', {
            type: 'http',
            backend: {
                rel: 'ingest_providers'
            }
        });
    }]);

    return app;
});
