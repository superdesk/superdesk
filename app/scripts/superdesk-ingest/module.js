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
        'superdesk.search',
        'superdesk.dashboard',
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
        },
        afp: {
            label: 'AFP',
            templateUrl: require.toUrl('./views/settings/afpConfig.html')
        }
    });

    IngestProviderService.$inject = ['api', '$q'];
    function IngestProviderService(api, $q) {

        var service = {
            providers: null,
            providersLookup: {},
            fetched: null,
            fetchProviders: function() {
                var self = this;
                return api.ingestProviders.query().then(function(result) {
                    self.providers = result._items;
                });
            },
            generateLookup: function() {
                var self = this;

                this.providersLookup = _.indexBy(self.providers, '_id');

                return $q.when();
            },
            initialize: function() {
                if (!this.fetched) {

                    this.fetched = this.fetchProviders()
                        .then(angular.bind(this, this.generateLookup));
                }

                return this.fetched;
            }
        };
        return service;
    }
    app.service('ingestSources', IngestProviderService);

    app.config(['superdeskProvider', function(superdesk) {
        superdesk
            .activity('/workspace/ingest', {
                label: gettext('Workspace'),
                priority: 100,
                controller: require('./controllers/list'),
                templateUrl: require.toUrl('../superdesk-archive/views/list.html'),
                category: '/workspace',
                topTemplateUrl: require.toUrl('../superdesk-dashboard/views/workspace-topnav.html')
            })
            .activity('/settings/ingest', {
                label: gettext('Ingest Feed'),
                templateUrl: require.toUrl('./views/settings/settings.html'),
                controller: require('./controllers/settings'),
                category: superdesk.MENU_SETTINGS
            })
            .activity('archive', {
                label: gettext('Fetch'),
                icon: 'archive',
                controller: ['$timeout', 'api', 'data', function($timeout, api, data) {
                    var checkProgress = function(taskId, callback) {
                        var progress = 0;
                        api.archiveIngest.getById(taskId)
                        .then(function(result) {
                            if (result.state === 'SUCCESS') {
                                callback(100);
                            } else if (result.state === 'FAILURE') {
                                callback(null);
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
                        data.item.archiving = true;
                        data.item.archivingProgress = 0;
                        checkProgress(archiveItem.task_id, function(progress) {
                            if (progress === 100) {
                                data.item.archiving = false;
                                data.item.archived = true;
                            } else if (progress === null) {
                                data.item.archiving = false;
                                data.item.archiveError = true;
                                progress = 0;
                            }
                            data.item.archivingProgress = progress;
                        });
                    }, function(response) {
                        data.item.archiveError = true;
                    });
                }],
                filters: [
                    {action: 'list', type: 'ingest'}
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
