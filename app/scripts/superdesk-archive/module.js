define([
    'angular',
    'require',
    './controllers/archive',
    './controllers/edit'
], function(angular, require) {
    'use strict';

    var app = angular.module('superdesk.archive', []);

    app.config(['superdeskProvider', function(superdesk) {
        superdesk
            .permission('archive/write', {
                label: gettext('Manage archive'),
                permissions: {archive: {write: true}}
            })
            .permission('archive/read', {
                label: gettext('Read archive'),
                permissions: {archive: {read: true}}
            });
    }]);

    app.config(['superdeskProvider', function(superdesk) {
        superdesk
            .activity('/archive', {
                label: gettext('Archive'),
                priority: -700,
                templateUrl: require.toUrl('./views/archive.html'),
                controller: require('./controllers/archive'),
                category: superdesk.MENU_MAIN,
                reloadOnSearch: false
            })
            .activity('/edit', {
                templateUrl: require.toUrl('./views/edit.html'),
                controller: require('./controllers/edit'),
                filters: [
                    {action: 'edit', type: 'archive'}
                ]
            })
            .activity('start-edit', {
                label: gettext('Edit'),
                icon: 'edit',
                controller: ['workqueue', 'data', 'resolve', function(queue, data, resolve) {
                    queue.add(data);
                    resolve(data);
                }],
                filters: [{action: 'list', type: 'archive'}]
            })
            .activity('archive', {
                label: gettext('Archive'),
                icon: 'archive',
                controller: ['em', 'superdesk', 'data', 'resolve', function(em, superdesk, data, resolve) {
                    if (!data.archived) {
                        em.create('archive', data).then(function(item) {
                            delete data.archiving;
                            data.archived = item.archived;
                            resolve(item);
                        });

                        data.archiving = true; // set after create not to send it as part of data
                    } else {
                        superdesk.data('archive').find(data._id).then(function(item) {
                            resolve(item);
                        });
                    }
                }],
                filters: [
                    {action: 'archive', type: 'ingest'}
                ]
            })
            .activity('fetch', {
                label: gettext('Fetch'),
                icon: 'expand',
                controller: ['data', 'workqueue', 'superdesk', 'resolve', function(data, queue, superdesk, resolve) {
                    var edit = function() {
                        superdesk.intent('archive', 'ingest', data).then(function(item) {
                            queue.add(item);
                            resolve(item);
                        });
                    };

                    if (data.archived) {
                        edit();
                    } else {
                        superdesk.intent('fetch', 'ingest', data).then(edit);
                    }
                }],
                filters: [
                    {action: 'list', type: 'ingest'}
                ]
            })
            .activity('fetch-article', {
                label: gettext('as Article'),
                controller: ['data', 'resolve', function(data, resolve) {
                    console.log('fetch as article');
                    resolve(data);
                }],
                filters: [
                    {action: 'fetch', type: 'ingest'}
                ]
            })
            .activity('fetch-factbox', {
                label: gettext('as Factbox'),
                controller: ['data', 'resolve', function(data, resolve) {
                    console.log('fetch as factbox', data);
                    resolve(data);
                }],
                filters: [
                    {action: 'fetch', type: 'ingest'}
                ]
            })
            .activity('fetch-sidebar', {
                label: gettext('as Sidebar'),
                controller: ['data', 'resolve', function(data, resolve) {
                    console.log('fetch as sidebar', data);
                    resolve(data);
                }],
                filters: [
                    {action: 'fetch', type: 'ingest'}
                ]
            });
    }]);

    /**
     * Subjectcodes loader
     */
    app.service('subjectcodes', ['superdesk', function(superdesk) {
        this.load = function() {
            return superdesk.data('subjectcodes').query().then(function(codes) {
                return codes._items;
            });
        };
    }]);
});
