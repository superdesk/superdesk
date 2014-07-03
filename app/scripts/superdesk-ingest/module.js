define([
    'angular',
    'require',
    './controllers/list',
    './controllers/settings',
    './ingest-widget/ingest',
    './ingest-stats-widget/stats',
    './directives'
], function(angular, require) {
    'use strict';

    var app = angular.module('superdesk.ingest', [
        'superdesk.widgets.ingest',
        'superdesk.widgets.ingeststats',
        require('./directives').name
    ]);

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
                controller: ['$timeout', 'api', 'data', function($timeout, api, data) {
                    var checkProgress = function(taskId, callback) {
                        var progress = 0;
                        api.archiveIngest.getById(taskId)
                        .then(function(result) {
                            if (result.state === 'SUCCESS') {
                                callback(100);
                            } else if (result.state === 'PROGRESS') {
                                var newProgress = Math.floor(parseInt(result.current || 0, 10) * 100 / parseInt(result.total, 10));
                                if (progress !== newProgress) {
                                    progress = newProgress;
                                    callback(progress);
                                }
                                if (progress !== 100) {
                                    $timeout(function() {
                                        checkProgress(taskId, callback);
                                    }, 1000);
                                }
                            }
                        });
                    };

                    api.archiveIngest.create({
                        guid: data.item.guid
                    })
                    .then(function(archiveItem) {
                        data.list[data.index].archiving = true;
                        data.list[data.index].archivingProgress = 0;
                        checkProgress(archiveItem.task_id, function(progress) {
                            data.list[data.index].archivingProgress = progress;
                            if (progress === 100) {
                                data.list[data.index].archiving = false;
                                data.list[data.index].archived = true;
                            }
                        });
                    }, function(response) {
                        data.list[data.index].archiveError = true;
                    });
                }],
                filters: [
                    {action: 'archive', type: 'ingest'}
                ]
            });
    }]);

    app.config(['apiProvider', function(apiProvider) {
        apiProvider.api('archiveIngest', {
            type: 'http',
            backend: {
                rel: 'archive_ingest'
            }
        });
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
