define([
    'angular',
    'require',
    './upload-controller',
    './controllers/list',
    '../superdesk-items-common/module'
], function(angular, require) {
    'use strict';

    var app = angular.module('superdesk.media', [
        require('../superdesk-items-common/module').name]
    );

    app.config(['superdeskProvider', function(superdesk) {
        superdesk
            .activity('/media/', {
                label: gettext('Media'),
                priority: 100,
                controller: require('./controllers/list'),
                templateUrl: require.toUrl('./views/list.html'),
                category: superdesk.MENU_MAIN,
                reloadOnSearch: false,
                beta: true
            })
            .activity('upload.media', {
                label: gettext('Upload media'),
                modal: true,
                cssClass: 'upload-media responsive-popup',
                controller: require('./upload-controller'),
                templateUrl: require.toUrl('./views/upload-media.html'),
                filters: [
                    {action: 'upload', type: 'media'}
                ]
            });
    }]);

    app.config(['apiProvider', function(apiProvider) {
        apiProvider.api('image', {
            type: 'http',
            backend: {
                rel: 'Content/ItemImage',
                headers: {'X-Filter': 'Item.*, ItemImage.*'}
            }
        });
    }]);
});
