define([
    'angular',
    'require',
    './controllers/list',
    './controllers/upload',
    './archive-widget/archive',
    './directives'
], function(angular, require) {
    'use strict';

    ContentQueryBuilder.$inject = ['$location'];
    function ContentQueryBuilder($location) {

        /**
         * Single query instance
         *
         * @param {string} q Query string query
         */
        function Query(q) {
            var size = 25;
            var sort = [{versioncreated: 'desc'}];
            var filters = [];

            /**
             * Get criteria for given query
             */
            this.getCriteria = function getCriteria() {
                var criteria = {
                    query: {filtered: {filter: {and: filters}}},
                    size: size,
                    sort: sort
                };

                if (q) {
                    criteria.query.filtered.query = {query_string: {query: q}};
                }

                return criteria;
            };

            /**
             * Add filter to query
             *
             * @param {Object} filter
             */
            this.filter = function addFilter(filter) {
                filters.push(filter);
                return this;
            };

            /**
             * Set size
             *
             * @param {number} _size
             */
            this.size = function setSize(_size) {
                size = _size != null ? _size : size;
                return this;
            };

            /**
             * Set query string query
             *
             * @param {string} _q
             */
            this.q = function setQ(_q) {
                q = _q || null;
                return this;
            };

            // do base filtering
            if ($location.search().spike) {
                this.filter({term: {is_spiked: true}});
            } else {
                this.filter({not: {term: {is_spiked: true}}});
            }
        }

        /**
         * Start creating a new query
         *
         * @param {string} q
         */
        this.query = function createQuery(q) {
            return new Query(q);
        };
    }

    SpikeService.$inject = ['$location', 'api', 'notify', 'gettext'];
    function SpikeService($location, api, notify, gettext) {
        var RESOURCE = 'archive_spike';

        /**
         * Spike given item.
         *
         * @param {Object} item
         */
        this.spike = function spike(item) {
            return api.save(RESOURCE, {is_spiked: true}, null, item)
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
            return api.remove(item, null, RESOURCE).then(function() {
                notify.success(gettext('Item was unspiked.'));
            });
        };
    }

    return angular.module('superdesk.archive', [
        require('./directives').name,
        'superdesk.dashboard',
        'superdesk.widgets.archive'
        ])

        .service('spike', SpikeService)
        .service('contentQuery', ContentQueryBuilder)

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
                    ]
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
                .activity('spike', {
                    label: gettext('Spike Item'),
                    icon: 'remove',
                    controller: ['spike', 'data', function spikeActivity(spike, data) {
                        return spike.spike(data.item);
                    }],
                    filters: [{action: superdesk.ACTION_EDIT, type: 'archive'}]
                })
                .activity('unspike', {
                    label: gettext('Unspike Item'),
                    icon: 'remove',
                    controller: ['spike', 'data', function unspikeActivity(spike, data) {
                        return spike.unspike(data.item);
                    }],
                    filters: [{action: superdesk.ACTION_EDIT, type: 'spike'}]
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
        }])

        /**
         * Item filters sidebar
         */
        .directive('sdItemFilters', function() {
            return {
                templateUrl: 'scripts/superdesk-archive/views/item-filters.html',
                link: function(scope) {
                    scope.sTab = true;
                }
            };
        })

        /**
         * Item list with sidebar preview
         */
        .directive('sdItemList', function() {
            return {
                templateUrl: 'scripts/superdesk-archive/views/item-list.html'
            };
        })

        /**
         * Edit item view
         */
        .directive('sdEditView', function() {
            return {
                templateUrl: 'scripts/superdesk-archive/views/edit-view.html'
            };
        })
        ;
});
