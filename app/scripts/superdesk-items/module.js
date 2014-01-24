define([
    'jquery',
    'angular',
    'require',
    'angular-slider',
    './resources',
    './controllers/ingest',
    './controllers/settings',
    './controllers/edit',
    './controllers/ref',
    './directives',
    './filters',
    './services',
    './ingest-widget/ingest',
    './stats-widget/stats',
    './panes/info/info'
], function($, angular, require) {
    'use strict';

    var app = angular.module('superdesk.items', [
        'superdesk.items.resources',
        'superdesk.items.directives',
        'superdesk.items.filters',
        'superdesk.items.services',
        'superdesk.widgets.ingest',
        'superdesk.widgets.ingeststats',
        'superdesk.panes.info',
        'uiSlider'
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
            });
    }]);

    app.config(['superdeskProvider', function(superdesk) {
        superdesk
            .activity('/ingest', {
                when: '/ingest/:id?',
                label: gettext('Ingest'),
                templateUrl: 'scripts/superdesk-items/views/ingest.html',
                controller: require('./controllers/ingest'),
                priority: -500,
                category: superdesk.MENU_MAIN,
                filters: [
                    {
                        action: superdesk.ACTION_VIEW,
                        type: 'ingest'
                    }
                ]
            })
            .activity('/edit', {
                templateUrl: 'scripts/superdesk-items/views/edit.html',
                controller: require('./controllers/edit'),
                filters: [
                    {action: 'edit', type: 'ingest'}
                ]
            })
            .activity('/settings/ingest', {
                label: gettext('Ingest Feed'),
                templateUrl: 'scripts/superdesk-items/views/settings/settings.html',
                controller: require('./controllers/settings'),
                category: superdesk.MENU_SETTINGS
            })
            .activity('fetch', {
                label: gettext('Fetch'),
                icon: 'expand',
                controller: ['data', 'workqueue', 'superdesk', function(data, queue, superdesk) {
                    superdesk.intent('fetch', 'ingest', data).then(function() {
                        console.log('add to queue');
                        queue.add(data);
                    });
                }],
                filters: [
                    {action: 'list', type: 'ingest'}
                ]
            })
            .activity('fetch-article', {
                label: gettext('as Article'),
                controller: ['data', function(data) {
                    console.log('fetch as article');
                }],
                filters: [
                    {action: 'fetch', type: 'ingest'}
                ]
            })
            .activity('fetch-factbox', {
                label: gettext('as Factbox'),
                controller: ['data', function(data) {
                    console.log('fetch as factbox', data);
                }],
                filters: [
                    {action: 'fetch', type: 'ingest'}
                ]
            })
            .activity('fetch-sidebar', {
                label: gettext('as Sidebar'),
                controller: ['data', function(data) {
                    console.log('fatch as sidebar', data);
                }],
                filters: [
                    {action: 'fetch', type: 'ingest'}
                ]
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
