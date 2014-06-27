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
            })
            .activity('delete.archive', {
                label: gettext('Delete archive'),
                confirm: gettext('Please confirm you want to delete an archive item.'),
                icon: 'remove',
                controller: ['$location', 'api', 'notify', 'data', function($location, api, notify, data) {
                    return api.archive.remove(data.item).then(function(response) {
                        if ($location.search()._id === data.item._id) {
                            $location.search('_id', null);
                        }
                        data.list.splice(data.index, 1);
                    }, function(response) {
                        notify.error(gettext('I\'m sorry but can\'t delete the archive item right now.'));
                    });
                }],
                filters: [
                    {action: superdesk.ACTION_EDIT, type: 'archive'}
                ]
            });
    }]);

    app.config(['apiProvider', function(apiProvider) {
    	apiProvider.api('notification', {
            type: 'http',
            backend: {
                rel: 'notification'
            }
        });
        apiProvider.api('archive', {
            type: 'http',
            backend: {
                rel: 'archive'
            }
        });
        apiProvider.api('archiveMedia', {
            type: 'http',
            backend: {
                rel: 'archive_media'
            }
        });
    }]);

    return app;
});
