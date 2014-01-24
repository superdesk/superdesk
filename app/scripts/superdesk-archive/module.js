define([
    'angular',
    'require',
    'view',
    './controllers/archive'
], function(angular, require, view) {
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
                templateUrl: view('archive.html', app),
                controller: require('./controllers/archive'),
                category: superdesk.MENU_MAIN,
                reloadOnSearch: false
            })
            .activity('archive', {
                label: gettext('Archive'),
                icon: 'archive',
                controller: ['em', 'data', function(em, data) {
                    if (!data.archived) {
                        em.create('archive', data).then(function(item) {
                            data.archived = item.archived;
                            delete data.archiving;
                        });

                        data.archiving = true; // set after create not to send it as part of data
                    }
                }],
                filters: [
                    {action: 'list', type: 'ingest'}
                ]
            });
    }]);
});
