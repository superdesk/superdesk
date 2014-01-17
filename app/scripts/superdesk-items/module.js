define([
    'jquery',
    'angular',
    'require',
    './resources',
    './controllers/ingest',
    './controllers/archive',
    './controllers/settings',
    './controllers/edit',
    './controllers/ref',
    './directives',
    './filters',
    './ingest-widget/ingest',
    './stats-widget/stats',
    './panes/info/info'
], function($, angular, require) {
    'use strict';

    var app = angular.module('superdesk.items', [
        'superdesk.items.resources',
        'superdesk.items.directives',
        'superdesk.items.filters',
        'superdesk.widgets.ingest',
        'superdesk.widgets.ingeststats',
        'superdesk.panes.info'
    ]);

    app.controller('RefController', require('./controllers/ref'));

    app.value('providerTypes', {
        aap: {
            label: 'AAP',
            templateUrl: 'scripts/superdesk-items/views/settings/aapConfig.html'
        },
        reuters: {
            label: 'Reuters',
            templateUrl: 'scripts/superdesk-items/views/settings/reutersConfig.html'
        }
    });

    app.config(['superdeskProvider', function(superdesk) {
        superdesk
            .permission('items-manage', {
                label: gettext('Manage ingest items'),
                permissions: {items: {write: true}}
            })
            .permission('items-read', {
                label: gettext('Read ingest items'),
                permissions: {items: {read: true}}
            })
            .permission('archive-manage', {
                label: gettext('Manage archive'),
                permissions: {archive: {write: true}}
            })
            .permission('archive-read', {
                label: gettext('Read archive'),
                permissions: {archive: {read: true}}
            });
    }]);

    app.config(['superdeskProvider', function(superdesk) {
        /**
         * Resolve ingest/archive list
         */
        function resolve(resource) {
            return {
                items: ['locationParams', 'em', '$route', function(locationParams, em, $route) {
                    var where;

                    if ('provider' in $route.current.params) {
                        where = {
                            provider: $route.current.params.provider
                        };
                    }

                    var criteria = locationParams.reset({
                        where: where,
                        sort: ['firstcreated', 'desc'],
                        max_results: 25
                    });

                    return em.getRepository(resource).matching(criteria);
                }]
            };
        }

        function resolveArticles() {
            return {
                articles : ['server', 'storage', '$q', function(server,storage,$q) {

                    var inprogress = storage.getItem('collection:inprogress') || {};
                    var openedArticles = [];
                    var resolved = 0;
                    var deferred = $q.defer();

                    angular.forEach(inprogress.opened, function(article_id, key) {
                        server.readById('ingest',article_id).then(function(data){
                            openedArticles[key]= data;
                            resolved++;
                            if (resolved === inprogress.opened.length) {
                                deferred.resolve(openedArticles);
                            }
                        });
                    });

                    return deferred.promise;
                }],
                item: ['$route', 'server', function($route, server) {
                    return server.readById('ingest', $route.current.params.id);
                }]
            };
        }

        superdesk
            .activity('ingest', {
                when: '/ingest/:id?',
                href: '/ingest/',
                label: gettext('Ingest'),
                templateUrl: 'scripts/superdesk-items/views/ingest.html',
                controller: require('./controllers/ingest'),
                resolve: resolve('ingest'),
                priority: -800,
                category: superdesk.MENU_MAIN
            })
            .activity('archive', {
                when: '/archive/',
                label: gettext('Archive'),
                priority: -700,
                templateUrl: 'scripts/superdesk-items/views/archive.html',
                controller: require('./controllers/archive'),
                resolve: resolve('archive'),
                category: superdesk.MENU_MAIN
            })
            .activity('archive-detail', {
                when: '/article/:id',
                templateUrl: 'scripts/superdesk-items/views/edit.html',
                controller: require('./controllers/edit'),
                resolve: resolveArticles()
            })
            .activity('settings-ingest', {
                when: '/settings/ingest',
                label: gettext('Ingest Feed'),
                templateUrl: 'scripts/superdesk-items/views/settings/settings.html',
                controller: require('./controllers/settings'),
                category: superdesk.MENU_SETTINGS
            });
    }]);

    app.filter('characterCount', function() {
        return function(input) {
            return $(input).text().length;
        };
    });

    app.filter('wordCount', function() {
        var nonchar = /[^\w]/g;
        var whitesp = /\s+/;
        return function(input) {
            var text = $(input).text();
            return text.replace(nonchar, ' ').split(whitesp).length;
        };
    });
});
