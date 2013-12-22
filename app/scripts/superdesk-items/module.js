define([
    'jquery',
    'angular',
    'angular-ui',
    'superdesk/server',
    'superdesk/entity',
    './resources',
    './controllers/ingest',
    './controllers/archive',
    './controllers/settings',
    './controllers/edit',
    './controllers/ref',
    './directives',
    './filters',
    './ingest-widget/ingest',
    './stats-widget/stats'
], function($, angular) {
    'use strict';

    angular.module('superdesk.items', [
        'superdesk.entity',
        'superdesk.items.resources',
        'superdesk.items.directives',
        'superdesk.items.filters',
        'ui.bootstrap',
        'superdesk.widgets.ingest',
        'superdesk.widgets.ingeststats'
    ])
        .controller('SettingsCtrl', require('superdesk-items/controllers/settings'))
        .controller('RefController', require('superdesk-items/controllers/ref'))
        .value('providerTypes', {
            aap: {
                label: 'AAP',
                templateUrl: 'scripts/superdesk-items/views/settings/aapConfig.html'
            },
            reuters: {
                label: 'Reuters',
                templateUrl: 'scripts/superdesk-items/views/settings/reutersConfig.html'
            }
        })
        .config(function(permissionsProvider) {
            permissionsProvider.permission('items-manage', {
                label: gettext('Manage ingest items'),
                permissions: {items: {write: true}}
            });
            permissionsProvider.permission('items-read', {
                label: gettext('Read ingest items'),
                permissions: {items: {read: true}}
            });
            permissionsProvider.permission('archive-manage', {
                label: gettext('Manage archive'),
                permissions: {archive: {write: true}}
            });
            permissionsProvider.permission('archive-read', {
                label: gettext('Read archive'),
                permissions: {archive: {read: true}}
            });
        })
        .config(function(activityProvider) {
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

            activityProvider
                .activity('ingest', {
                    href: '/ingest/:id?',
                    menuHref: '/ingest/',
                    label: gettext('Ingest'),
                    templateUrl: 'scripts/superdesk-items/views/ingest.html',
                    controller: require('superdesk-items/controllers/ingest'),
                    resolve: resolve('ingest'),
                    priority: -300
                })
                .activity('archive', {
                    href: '/archive/',
                    label: gettext('Archive'),
                    priority: -200,
                    templateUrl: 'scripts/superdesk-items/views/archive.html',
                    controller: require('superdesk-items/controllers/archive'),
                    resolve: resolve('archive')
                })
                .activity('archive-detail', {
                    href: '/archive/:id',
                    label: gettext('Archive'),
                    menu: false,
                    templateUrl: 'scripts/superdesk-items/views/edit.html',
                    controller: require('superdesk-items/controllers/edit'),
                    resolve: {
                        item: ['$route', 'server', function($route, server) {
                            return server.readById('items', $route.current.params.id);
                        }]
                    }
                });
        })
        .config(function(settingsProvider) {
            settingsProvider.register('ingest-feed', {
                label: gettext('Ingest Feed'),
                templateUrl: 'scripts/superdesk-items/views/settings/settings.html'
            });
        })
        .filter('characterCount', function() {
            return function(input) {
                return $(input).text().length;
            };
        })
        .filter('wordCount', function() {
            var nonchar = /[^\w]/g;
            var whitesp = /\s+/;
            return function(input) {
                var text = $(input).text();
                return text.replace(nonchar, ' ').split(whitesp).length;
            };
        });
});
