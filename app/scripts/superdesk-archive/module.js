define([
    'angular',
    'require',
    './controllers/list',
    './controllers/upload',
    './archive-widget/archive',
    './directives'
], function(angular, require) {
    'use strict';

    SpikeService.$inject = ['$location', 'api', 'notify', 'gettext'];
    function SpikeService($location, api, notify, gettext) {
        var SPIKE_RESOURCE = 'archive_spike',
            UNSPIKE_RESOURCE = 'archive_unspike';

        /**
         * Spike given item.
         *
         * @param {Object} item
         */
        this.spike = function spike(item) {
            return api.update(SPIKE_RESOURCE, item, {state: 'spiked'})
                .then(function() {
                    if ($location.search()._id === item._id) {
                        $location.search('_id', null);
                    }
                    notify.success(gettext('Item was spiked.'));
                }, function(response) {
                    notify.error(gettext('I\'m sorry but can\'t delete the archive item right now.'));
                });
        };

        /**
         * Unspike given item.
         *
         * @param {Object} item
         */
        this.unspike = function unspike(item) {
            return api.update(UNSPIKE_RESOURCE, item, {})
                .then(function() {
                    notify.success(gettext('Item was unspiked.'));
                });
        };
    }

    return angular.module('superdesk.archive', [
        'superdesk.search',
        require('./directives').name,
        'superdesk.dashboard',
        'superdesk.widgets.archive'
    ])

        .service('spike', SpikeService)

        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/workspace/content', {
                    label: gettext('Workspace'),
                    priority: 100,
                    controller: require('./controllers/list'),
                    templateUrl: require.toUrl('./views/list.html'),
                    topTemplateUrl: require.toUrl('../superdesk-dashboard/views/workspace-topnav.html'),
                    filters: [
                        {action: 'view', type: 'content'}
                    ],
                    privileges: {archive: 1}
                })
                .activity('upload.media', {
                    label: gettext('Upload media'),
                    modal: true,
                    cssClass: 'upload-media responsive-popup',
                    controller: require('./controllers/upload'),
                    templateUrl: require.toUrl('./views/upload.html'),
                    filters: [
                        {action: 'upload', type: 'media'}
                    ],
                    privileges: {archive: 1}
                })
                .activity('spike', {
                    label: gettext('Spike Item'),
                    icon: 'remove',
                    controller: ['spike', 'data', function spikeActivity(spike, data) {
                        return spike.spike(data.item);
                    }],
                    filters: [{action: 'list', type: 'archive'}],
                    action: 'spike'
                })
                .activity('unspike', {
                    label: gettext('Unspike Item'),
                    icon: 'revert',
                    controller: ['spike', 'data', function unspikeActivity(spike, data) {
                        return spike.unspike(data.item);
                    }],
                    filters: [{action: 'list', type: 'spike'}],
                    action: 'unspike'
                });
        }])

        .config(['apiProvider', function(apiProvider) {
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
});
