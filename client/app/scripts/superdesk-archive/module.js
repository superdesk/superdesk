define([
    'angular',
    'require',
    './controllers/list',
    './controllers/upload',
    './archive-widget/archive',
    './related-item-widget/relatedItem',
    './directives'
], function(angular, require) {
    'use strict';

    MultiService.$inject = ['$rootScope'];
    function MultiService($rootScope) {

        var items = [];

        /**
         * Test if given item is selected
         *
         * @param {Object} item
         */
        this.isSelected = function(item) {
            return item.selected;
        };

        /**
         * Toggle item selected state
         *
         * @param {Object} item
         */
        this.toggle = function(item) {
            if (item.selected) {
                items = _.union(items, [item]);
            } else {
                items = _.without(items, item);
            }
            this.count = items.length;
        };

        /**
         * Get list of selected items identifiers
         */
        this.getIds = function() {
            return _.map(items, '_id');
        };

        /**
         * Get list of selected items
         */
        this.getItems = function() {
            return items;
        };

        /**
         * Reset to empty
         */
        this.reset = function() {
            _.each(items, function(item) {
                item.selected = false;
            });

            items = [];
            this.count = 0;
        };

        // main
        this.reset();
        $rootScope.$on('$routeChangeStart', angular.bind(this, this.reset));
    }

    SpikeService.$inject = ['$location', 'api', 'notify', 'gettext'];
    function SpikeService($location, api, notify, gettext) {
        var SPIKE_RESOURCE = 'archive_spike',
            UNSPIKE_RESOURCE = 'archive_unspike';

        /**
         * Spike given item.
         *
         * @param {Object} item
         */
        this.spike = function(item) {
            return api.update(SPIKE_RESOURCE, item, {state: 'spiked'})
                .then(function() {
                    if ($location.search()._id === item._id) {
                        $location.search('_id', null);
                    }
                }, function(response) {
                    item.error = response;
                    if (angular.isDefined(response.data._issues) &&
                        angular.isDefined(response.data._issues['validator exception'])) {
                        notify.error(gettext(response.data._issues['validator exception']));
                    }
                })
                ['finally'](function() {
                    item.actioning.spike = false;
                });
        };

        /**
         * Spike given items.
         *
         * @param {Object} items
         */
        this.spikeMultiple = function spikeMultiple(items) {
            items.forEach(this.spike);
        };

        /**
         * Unspike given item.
         *
         * @param {Object} item
         */
        this.unspike = function(item) {
            return api.update(UNSPIKE_RESOURCE, item, {})
                .then(function() {
                    if ($location.search()._id === item._id) {
                        $location.search('_id', null);
                    }
                }, function(response) {
                    item.error = response;
                })
                ['finally'](function() {
                    item.actioning.unspike = false;
                });
        };

        /**
         * Unspike given items.
         *
         * @param {Object} items
         */
        this.unspikeMultiple = function unspikeMultiple(items) {
            items.forEach(this.unspike);
        };
    }

    ArchiveService.$inject = ['desks', 'session', 'api', '$q'];
    function ArchiveService(desks, session, api, $q) {
        /**
         * Adds 'task' property to the article represented by item.
         *
         * @param {Object} item
         */
        this.addTaskToArticle = function (item) {
            if ((!item.task || !item.task.desk) && desks.activeDeskId && desks.userDesks) {
                var currentDesk = _.find(desks.userDesks._items, {_id: desks.activeDeskId});
                item.task = {'desk': desks.activeDeskId, 'stage': currentDesk.incoming_stage, 'user': session.identity._id};
            }
        };

        /**
         * Returns the type of the item.
         *
         * @param {Object} item
         * @return String
         *      'ingest' if the state of the item is Ingested
         *      'spike' if the state of the item is Spiked
         *      'archived' if the state of the item is Published and allow_post_publish_actions is false
         *      'archive' if none of the above is returned
         */
        this.getType = function(item) {
            var itemType;
            if (this.isLegal(item)) {
                itemType = item._type;
            } else if (item._type === 'externalsource') {
                itemType = 'externalsource';
            } else if (item.state === 'spiked') {
                itemType = 'spike';
            } else if (item.state === 'ingested') {
                itemType = 'ingest';
            } else {
                var isPublished = this.isPublished(item);

                if (!isPublished || (isPublished && item.allow_post_publish_actions === true)) {
                    itemType = 'archive';
                } else if (isPublished && item.allow_post_publish_actions === false) {
                    itemType = 'archived';
                }
            }

            return itemType;
        };

        /**
         * Returns true if the item is fetched from Legal Archive
         *
         * @param {Object} item
         * @return boolean if the item is fetched from Legal Archive, false otherwise.
         */
        this.isLegal = function(item) {
            return (angular.isDefined(item._type) && !_.isNull(item._type) && item._type === 'legal_archive');
        };

        /**
         * Returns true if the state of the item is in one of the published states - Scheduled, Published, Corrected
         * and Killed.
         *
         * @param {Object} item
         * @return true if the state of the item is in one of the published states, false otherwise.
         */
        this.isPublished = function(item) {
            return _.contains(['published', 'killed', 'scheduled', 'corrected'], item.state);
        };

        /***
         * Returns version history of the item.
         *
         * @param {Object} item
         * @param {Object} desks deskService
         * @param {String} historyType one of versions, operations
         * @return list of object where each object is a version of the item
         */
        this.getVersionHistory = function(item, desks, historyType) {
            if (this.isLegal(item)) {
                return api.legal_archive_versions.getByUrl(item._links.collection.href + '_versions?_id=' + item._id)
                    .then(function(result) {
                        _.each(result._items, function(version) {
                            version.desk = version.task.desk;
                            version.stage = version.task.stage;
                            version.creator = version.version_creator || version.original_creator;

                            if (version.type === 'text' || version.type === 'preformatted') {
                                version.typeName = 'Story';
                            } else {
                                version.typeName = _.capitalize(item.type);
                            }
                        });

                        if (historyType === 'versions') {
                            return $q.when(_.sortBy(_.reject(result._items, {version: 0}), '_current_version').reverse());
                        } else if (historyType === 'operations') {
                            return $q.when(_.sortBy(result._items, '_current_version'));
                        }
                    });
            } else {
                return api.archive.getByUrl(item._links.self.href + '?version=all&embedded={"user":1}')
                    .then(function(result) {
                        _.each(result._items, function(version) {
                            if (version.task) {
                                if (version.task.desk) {
                                    var versiondesk = desks.deskLookup[version.task.desk];
                                    version.desk = versiondesk && versiondesk.name;
                                }
                                if (version.task.stage) {
                                    var versionstage = desks.stageLookup[version.task.stage];
                                    version.stage = versionstage && versionstage.name;
                                }
                            }
                            if (version.version_creator || version.original_creator) {
                                var versioncreator = desks.userLookup[version.version_creator || version.original_creator];
                                version.creator = versioncreator && versioncreator.display_name;
                            }

                            if (version.type === 'text' || version.type === 'preformatted') {
                                version.typeName = 'Story';
                            } else {
                                version.typeName = _.capitalize(item.type);
                            }
                        });

                        if (historyType === 'versions') {
                            return $q.when(_.sortBy(_.reject(result._items, {version: 0}), '_current_version').reverse());
                        } else if (historyType === 'operations') {
                            return $q.when(_.sortBy(result._items, '_current_version'));
                        }
                    });
            }
        };

        /**
         * Get latest version from the list
         *
         * @param {Object} item
         * @param {Object} versions
         * @return last version of the item
         */
        this.lastVersion = function(item, versions) {
            if (item._latest_version) {
                return _.find(versions, {_current_version: item._latest_version});
            }

            return _.max(versions, function(version) {
                return version._current_version || version.version || version._updated;
            });
        };
    }

    return angular.module('superdesk.archive', [
        'superdesk.search',
        'superdesk.archive.directives',
        'superdesk.dashboard',
        'superdesk.widgets.archive',
        'superdesk.widgets.relatedItem'
    ])

        .service('spike', SpikeService)
        .service('multi', MultiService)
        .service('archiveService', ArchiveService)
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/workspace/content', {
                    label: gettext('Workspace'),
                    priority: 100,
                    controller: require('./controllers/list'),
                    templateUrl: require.toUrl('./views/list.html'),
                    topTemplateUrl: require.toUrl('../superdesk-dashboard/views/workspace-topnav.html'),
                    sideTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-sidenav.html',
                    filters: [
                        {action: 'view', type: 'content'}
                    ],
                    privileges: {archive: 1}
                })
                .activity('upload.media', {
                    label: gettext('Upload media'),
                    modal: true,
                    cssClass: 'upload-media modal-responsive',
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
                    monitor: true,
                    controller: ['spike', 'data', '$rootScope', function spikeActivity(spike, data, $rootScope) {
                        return spike.spike(data.item).then(function(item) {
                            $rootScope.$broadcast('item:spike');
                            return item;
                        });
                    }],
                    filters: [{action: 'list', type: 'archive'}],
                    action: 'spike',
                    condition: function(item) {
                        return (item.lock_user === null || angular.isUndefined(item.lock_user));
                    },
                    additionalCondition:['authoring', 'item', function(authoring, item) {
                        return authoring.itemActions(item).spike;
                    }]
                })
                .activity('unspike', {
                    label: gettext('Unspike Item'),
                    icon: 'unspike',
                    monitor: true,
                    controller: ['spike', 'data', '$rootScope', function unspikeActivity(spike, data, $rootScope) {
                        return spike.unspike(data.item).then(function(item) {
                            $rootScope.$broadcast('item:unspike');
                            return item;
                        });
                    }],
                    filters: [{action: 'list', type: 'spike'}],
                    action: 'unspike',
                    additionalCondition:['authoring', 'item', function(authoring, item) {
                        return authoring.itemActions(item).unspike;
                    }]
                })
                .activity('duplicate', {
                    label: gettext('Duplicate'),
                    icon: 'copy',
                    controller: ['$location', 'data', function($location, data) {
                        $location.search('fetch', data.item._id);
                    }],
                    filters: [{action: 'list', type: 'archive'}],
                    privileges: {duplicate: 1},
                    condition: function(item) {
                        return (item.lock_user === null || angular.isUndefined(item.lock_user));
                    },
                    additionalCondition:['authoring', 'item', function(authoring, item) {
                        return authoring.itemActions(item).duplicate;
                    }]
                })
                .activity('copy', {
                    label: gettext('Copy'),
                    icon: 'copy',
                    monitor: true,
                    controller: ['api', 'data', '$rootScope', function(api, data, $rootScope) {
                        api
                            .save('copy', {}, {}, data.item)
                            .then(function(archiveItem) {
                                data.item.task_id = archiveItem.task_id;
                                data.item.created = archiveItem._created;
                                $rootScope.$broadcast('item:copy');
                            }, function(response) {
                                data.item.error = response;
                            })
                        ['finally'](function() {
                            data.item.actioning.archiveContent = false;
                        });
                    }],
                    filters: [{action: 'list', type: 'archive'}],
                    condition: function(item) {
                        return item.lock_user === null || angular.isUndefined(item.lock_user);
                    },
                    additionalCondition:['authoring', 'item', function(authoring, item) {
                        return authoring.itemActions(item).copy;
                    }]
                })
                .activity('newtake', {
                    label: gettext('New Take'),
                    icon: 'plus-small',
                    filters: [{action: 'list', type: 'archive'}],
                    privileges: {archive: 1},
                    condition: function(item) {
                        return (item.lock_user === null || angular.isUndefined(item.lock_user));
                    },
                    additionalCondition:['authoring', 'item', function(authoring, item) {
                        return authoring.itemActions(item).new_take;
                    }],
                    controller: ['data', '$rootScope', 'desks', 'authoring', 'notify', 'superdesk',
                        function(data, $rootScope, desks, authoring, notify, superdesk) {
                            authoring.linkItem(data.item, null, desks.getCurrentDeskId())
                                .then(function(item) {
                                    notify.success(gettext('New take created.'));
                                    $rootScope.$broadcast('item:take');
                                    superdesk.intent('author', 'article', item);
                                }, function(response) {
                                    data.item.error = response;
                                    notify.error(gettext('Failed to generate new take.'));
                                });
                        }]
                })
                .activity('rewrite', {
                    label: gettext('Re-write'),
                    icon: 'multi-star-color',
                    filters: [{action: 'list', type: 'archive'}],
                    group: 'corrections',
                    privileges: {archive: 1},
                    condition: function(item) {
                        return (item.lock_user === null || angular.isUndefined(item.lock_user));
                    },
                    additionalCondition:['authoring', 'item', function(authoring, item) {
                        return authoring.itemActions(item).re_write;
                    }],
                    controller: ['data', '$location', 'api', 'notify', 'session', 'desks', 'superdesk',
                        function(data, $location, api, notify, session, desks, superdesk) {
                            session.getIdentity()
                                .then(function(user) {
                                    return api.save('archive_rewrite', {}, {}, data.item);
                                })
                                .then(function(new_item) {
                                    notify.success(gettext('Rewrite Created.'));
                                    superdesk.intent('author', 'article', new_item._id);
                                }, function(response) {
                                    if (angular.isDefined(response.data._message)) {
                                        notify.error(gettext('Failed to generate rewrite: ' + response.data._message));
                                    } else {
                                        notify.error(gettext('There is an error. Failed to generate rewrite.'));
                                    }
                                });
                        }]
                });
        }])

        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('copy', {
                type: 'http',
                backend: {
                    rel: 'copy'
                }
            });
            apiProvider.api('duplicate', {
                type: 'http',
                backend: {
                    rel: 'duplicate'
                }
            });
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
            apiProvider.api('archive_rewrite', {
                type: 'http',
                backend: {
                    rel: 'archive_rewrite'
                }
            });
            apiProvider.api('legal_archive_versions', {
                type: 'http',
                backend: {
                    rel: 'legal_archive_versions'
                }
            });
        }]);
});
