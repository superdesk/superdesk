(function() {
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
            items = _.without(items, _.find(items, identity));
            if (item.selected) {
                items = _.union(items, [item]);
            }

            this.count = items.length;

            function identity(_item) {
                return _item._id === item._id && _item._current_version === item._current_version;
            }
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
            var ids = [];
            _.each(items, function(item) {
                item.selected = false;
                ids.push(item._id);
            });
            $rootScope.$broadcast('multi:reset', items);
            items = [];
            this.count = 0;
            $rootScope.$broadcast('multi:reset', {ids: ids}); // let react know
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
                    return item;
                }, function(response) {
                    item.error = response;
                    if (angular.isDefined(response.data._issues) &&
                        angular.isDefined(response.data._issues['validator exception'])) {
                        notify.error(gettext(response.data._issues['validator exception']));
                    }
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
                    return item;
                }, function(response) {
                    item.error = response;
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

    ArchiveService.$inject = ['desks', 'session', 'api', '$q', 'search', '$location'];
    function ArchiveService(desks, session, api, $q, search, $location) {
        /**
         * Adds 'task' property to the article represented by item.
         *
         * @param {Object} item
         * @param {Object} desk when passed the item will be assigned to this desk instead of user's activeDesk.
         */
        this.addTaskToArticle = function (item, desk) {
            desk = desk || desks.getCurrentDesk();
            if ((!item.task || !item.task.desk) && desk && $location.path() !== '/workspace/personal') {
                item.task = {'desk': desk._id, 'stage': desk.working_stage, 'user': session.identity._id};
            }
        };

        /**
         * Returns the _type aka repository of the item.
         *
         * @param {Object} item
         * @return String
         *      'ingest' if the state of the item is Ingested
         *      'spike' if the state of the item is Spiked
         *      'archived' if item is archived (no post publish actions)
         *      'archive' if none of the above is returned
         */
        this.getType = function(item) {
            var itemType;
            if (this.isLegal(item)) {
                itemType = item._type;
            } else if (this.isArchived(item)) {
                itemType = 'archived';
            } else if (item._type === 'externalsource') {
                itemType = 'externalsource';
            } else if (item.state === 'spiked') {
                itemType = 'spike';
            } else if (item.state === 'ingested') {
                itemType = 'ingest';
            } else {
                itemType = 'archive';
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
            return item._type === 'legal_archive';
        };

        /**
         * Returns true if the item is fetched from Archived
         *
         * @param {Object} item
         * @return boolean if the item is fetched from Archived, false otherwise.
         */
        this.isArchived = function(item) {
            return item._type === 'archived';
        };

        /**
         *  Returns the list of items having the same slugline in the last day
         *  @param {String} slugline
         *  @return {Object} the list of archive items
         */
        this.getRelatedItems = function(slugline) {
            var before24HrDateTime = moment().subtract(1, 'days').format();
            var params = {};
            params.q = 'slugline:(' + slugline + ')';
            params.ignoreKilled = true;
            params.ignoreDigital = true;
            params.afterversioncreated = before24HrDateTime;

            var query = search.query(params);
            query.size(200);
            var criteria = query.getCriteria(true);
            criteria.repo = 'archive,published';

            return api.query('search', criteria).then(function(result) {
                return result;
            });
        };

        /**
         * Returns true if the state of the item is in one of the published states - Scheduled, Published, Corrected
         * and Killed.
         *
         * @param {Object} item
         * @return boolean if the state of the item is in one of the published states, false otherwise.
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
                return api.find('legal_archive', item._id, {version: 'all'})
                    .then(function(result) {
                        _.each(result._items, function(version) {
                            version.desk = version.task.desk;
                            version.stage = version.task.stage;
                            version.creator = version.version_creator || version.original_creator;

                            if (version.type === 'text') {
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
                return api.find('archive', item._id, {version: 'all', embedded: {user: 1}})
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

                            if (version.type === 'text') {
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

    UploadController.$inject = ['$scope', '$q', 'upload', 'api', 'archiveService', 'session'];
    function UploadController($scope, $q, upload, api, archiveService, session) {
        $scope.items = [];
        $scope.saving = false;
        $scope.failed = false;
        $scope.enableSave = false;
        $scope.currentUser =  session.identity;

        var requiredFields = ['headline', 'description', 'slugline'];

        var uploadFile = function(item) {
            var handleError = function(reason) {
                item.model = false;
                $scope.failed = true;
                return $q.reject(reason);
            };

            return item.upload || api.archive.getUrl()
                .then(function(url) {
                    item.upload = upload.start({
                        method: 'POST',
                        url: url,
                        data: {media: item.file},
                        headers: api.archive.getHeaders()
                    })
                    .then(function(response) {
                        if (response.data._issues) {
                            return handleError(response);
                        }

                        item.model = response.data;
                        return item;
                    }, handleError, function(progress) {
                        item.progress = Math.round(progress.loaded / progress.total * 100.0);
                    });

                    return item.upload;
                });
        };

        var checkFail = function() {
            $scope.failed = _.some($scope.items, {model: false});
        };

        var validateFields = function () {
            $scope.errorMessage = null;
            if (!_.isEmpty($scope.items)) {
                _.each($scope.items, function(item) {
                    _.each(requiredFields, function(key) {
                        if (item.meta[key] == null || _.isEmpty(item.meta[key])) {
                            $scope.errorMessage = 'Required field(s) are missing';
                            return false;
                        }
                    });
                });
            }
        };

        $scope.setAllMeta = function(field, val) {
            _.each($scope.items, function(item) {
                item.meta[field] = val;
            });
        };

        $scope.addFiles = function(files) {
            _.each(files, function(file) {
                var item = {
                    file: file,
                    meta: {byline: $scope.currentUser.byline},  // initialize meta.byline from user profile
                    progress: 0
                };
                item.cssType = item.file.type.split('/')[0];
                $scope.items.unshift(item);
                $scope.enableSave = true;
            });
        };

        $scope.upload = function() {
            var promises = [];
            _.each($scope.items, function(item) {
                if (!item.model && !item.progress) {
                    item.upload = null;
                    promises.push(uploadFile(item));
                }
            });
            if (promises.length) {
                return $q.all(promises);
            }
            return $q.when();
        };

        $scope.save = function() {
            validateFields();
            if ($scope.errorMessage == null) {
                $scope.saving = true;
                return $scope.upload().then(function(results) {
                    $q.all(_.map($scope.items, function(item) {
                        archiveService.addTaskToArticle(item.meta);
                        return api.archive.update(item.model, item.meta);
                    })).then(function(results) {
                        $scope.resolve(results);
                    });
                })
                ['finally'](function() {
                    $scope.saving = false;
                    checkFail();
                });
            }
        };

        $scope.cancel = function() {
            _.each($scope.items, $scope.cancelItem, $scope);
            $scope.reject();
        };

        $scope.tryAgain = function() {
            $scope.failed = null;
            $scope.upload();
        };

        $scope.cancelItem = function(item, index) {
            if (item != null) {
                if (item.model) {
                    api.archive.remove(item.model);
                } else if (item.upload && item.upload.abort) {
                    item.upload.abort();
                }
            }
            if (index !== undefined) {
                $scope.items.splice(index, 1);
            }
            if (_.isEmpty($scope.items)) {
                $scope.enableSave = false;
            }
            checkFail();
        };
    }

    return angular.module('superdesk.archive', [
        'superdesk.search',
        'superdesk.archive.directives',
        'superdesk.dashboard',
        'superdesk.widgets.base',
        'superdesk.widgets.relatedItem',
        'superdesk.archive.list'
    ])

        .service('spike', SpikeService)
        .service('multi', MultiService)
        .service('archiveService', ArchiveService)
        .controller('UploadController', UploadController)
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/workspace/content', {
                    label: gettext('Workspace'),
                    priority: 100,
                    controller: 'ArchiveListController',
                    templateUrl: 'scripts/superdesk-archive/views/list.html',
                    topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
                    sideTemplateUrl: 'scripts/superdesk-workspace/views/workspace-sidenav.html',
                    filters: [
                        {action: 'view', type: 'content'}
                    ],
                    privileges: {archive: 1}
                })
                .activity('upload.media', {
                    label: gettext('Upload media'),
                    modal: true,
                    cssClass: 'upload-media modal-responsive',
                    controller: UploadController,
                    templateUrl: 'scripts/superdesk-archive/views/upload.html',
                    filters: [
                        {action: 'upload', type: 'media'}
                    ],
                    privileges: {archive: 1}
                })
                .activity('spike', {
                    label: gettext('Spike Item'),
                    icon: 'trash',
                    monitor: true,
                    controller: ['spike', 'data', '$rootScope', function spikeActivity(spike, data, $rootScope) {
                        return spike.spike(data.item).then(function(item) {
                            $rootScope.$broadcast('item:spike');
                            return item;
                        });
                    }],
                    filters: [{action: 'list', type: 'archive'}],
                    action: 'spike',
                    keyboardShortcut: 'ctrl+x',
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
                    monitor: true,
                    controller: ['api', 'notify', '$rootScope', 'data', function(api, notify, $rootScope, data) {
                        api.save('duplicate', {}, {desk: data.item.task.desk}, data.item)
                            .then(function() {
                                $rootScope.$broadcast('item:duplicate');
                                notify.success(gettext('Item Duplicated'));
                            });
                    }],
                    filters: [{action: 'list', type: 'archive'}],
                    keyboardShortcut: 'ctrl+d',
                    privileges: {duplicate: 1},
                    condition: function(item) {
                        return (item.lock_user === null || angular.isUndefined(item.lock_user));
                    },
                    additionalCondition:['authoring', 'item', function(authoring, item) {
                        return authoring.itemActions(item).duplicate;
                    }]
                })
                .activity('createBroadcast', {
                    label: gettext('Create Broadcast'),
                    icon: 'broadcast',
                    monitor: true,
                    controller: ['api', 'notify', '$rootScope', 'data', 'desks', 'authoringWorkspace',
                    function(api, notify, $rootScope, data, desks, authoringWorkspace) {
                        api.save('archive_broadcast', {}, {desk: desks.getCurrentDeskId()}, data.item)
                            .then(function(broadcastItem) {
                                authoringWorkspace.edit(broadcastItem);
                                $rootScope.$broadcast('broadcast:created', {'item': data.item});
                            });
                    }],
                    filters: [{action: 'list', type: 'archive'}],
                    keyboardShortcut: 'ctrl+b',
                    privileges: {archive: 1},
                    condition: function(item) {
                        return (item.lock_user === null || angular.isUndefined(item.lock_user));
                    },
                    additionalCondition:['authoring', 'item', function(authoring, item) {
                        return authoring.itemActions(item).create_broadcast;
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
                    icon: 'new-doc',
                    filters: [{action: 'list', type: 'archive'}],
                    keyboardShortcut: 'ctrl+alt+t',
                    privileges: {archive: 1},
                    condition: function(item) {
                        return (item.lock_user === null || angular.isUndefined(item.lock_user));
                    },
                    additionalCondition:['authoring', 'item', function(authoring, item) {
                        return authoring.itemActions(item).new_take;
                    }],
                    controller: ['data', '$rootScope', 'desks', 'authoring', 'authoringWorkspace', 'notify', 'superdesk',
                        function(data, $rootScope, desks, authoring, authoringWorkspace, notify) {
                            // get the desk of the item to create the new take.
                            var deskId = null;
                            if (data.item.task && data.item.task.desk) {
                                deskId = data.item.task.desk;
                            }

                            authoring.linkItem(data.item, null, deskId)
                                .then(function(item) {
                                    notify.success(gettext('New take created.'));
                                    $rootScope.$broadcast('item:take');
                                    authoringWorkspace.edit(item);
                                }, function(response) {
                                    data.item.error = response;
                                    notify.error(gettext('Failed to generate new take.'));
                                });
                        }]
                })
                .activity('rewrite', {
                    label: gettext('Update'),
                    icon: 'edit-line',
                    filters: [{action: 'list', type: 'archive'}],
                    group: 'corrections',
                    privileges: {archive: 1},
                    condition: function(item) {
                        return (item.lock_user === null || angular.isUndefined(item.lock_user));
                    },
                    additionalCondition:['authoring', 'item', function(authoring, item) {
                        return authoring.itemActions(item).re_write;
                    }],
                    controller: ['data', '$location', 'api', 'notify', 'session', 'authoringWorkspace', 'desks', 'superdesk',
                        function(data, $location, api, notify, session, authoringWorkspace, desks, superdesk) {
                            session.getIdentity()
                                .then(function(user) {
                                    return api.save('archive_rewrite', {}, {}, data.item);
                                })
                                .then(function(new_item) {
                                    notify.success(gettext('Update Created.'));
                                    authoringWorkspace.edit(new_item._id);
                                }, function(response) {
                                    if (angular.isDefined(response.data._message)) {
                                        notify.error(gettext('Failed to generate update: ' + response.data._message));
                                    } else {
                                        notify.error(gettext('There is an error. Failed to generate update.'));
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
        }]);
})();

(function() {
    'use strict';

    var BaseListController = window.BaseListController;

    angular.module('superdesk.archive').controller('ArchiveListController', [
        '$scope', '$injector', '$location', '$q', '$timeout', 'superdesk',
        'session', 'api', 'desks', 'content', 'StagesCtrl', 'notify', 'multi',
    function ($scope, $injector, $location, $q, $timeout, superdesk, session, api, desks, content,
        StagesCtrl, notify, multi) {

        var resource,
            self = this;

        $injector.invoke(BaseListController, this, {$scope: $scope});
        $scope.currentModule = 'archive';
        $scope.stages = new StagesCtrl($scope);
        $scope.content = content;
        $scope.type = 'archive';
        $scope.repo = {
            ingest: false,
            archive: true
        };
        $scope.loading = false;
        $scope.spike = !!$location.search().spike;
        $scope.published = !!$location.search().published;

        $scope.togglePublished = function togglePublished() {
            if ($scope.spike) {
                $scope.toggleSpike();
            }

            $scope.published = !$scope.published;
            $location.search('published', $scope.published ? '1' : null);
            $location.search('_id', null);
            $scope.stages.select(null);
        };

        $scope.toggleSpike = function toggleSpike() {
            if ($scope.published) {
                $scope.togglePublished();
            }

            $scope.spike = !$scope.spike;
            $location.search('spike', $scope.spike ? 1 : null);
            $location.search('_id', null);
            $scope.stages.select(null);
        };

        $scope.stageSelect = function(stage) {
            if ($scope.spike) {
                $scope.toggleSpike();
            }

            if ($scope.published) {
                $scope.togglePublished();
            }

            $scope.stages.select(stage);
            multi.reset();
        };

        this.fetchItems = function fetchItems(criteria) {
            if (resource == null) {
                return;
            }
            $scope.loading = true;
            resource.query(criteria).then(function(items) {
                $scope.loading = false;
                $scope.items = items;
            }, function() {
                $scope.loading = false;
            });
        };

        this.fetchItem = function fetchItem(id) {
            if (resource == null) {
                return $q.reject(id);
            }

            return resource.getById(id);
        };

        var refreshPromise,
            refreshItems = function() {
                $timeout.cancel(refreshPromise);
                refreshPromise = $timeout(_refresh, 100, false);
            };

        function _refresh() {
            if (desks.active.desk) {
                if ($scope.published) {
                    resource = api('published');
                } else {
                    resource = api('archive');
                }
            } else {
                resource = api('user_content', session.identity);
            }
            self.refresh(true);
        }

        function reset(event, data) {
            if (data && data.item) {
                if ($location.search()._id === data.item) {
                    $location.search('_id', null);
                }
            }
            refreshItems();
        }

        $scope.$on('task:stage', function(_e, data) {
            if ($scope.stages.selected && (
                $scope.stages.selected._id === data.new_stage ||
                $scope.stages.selected._id === data.old_stage)) {
                refreshItems();
            }
        });

        $scope.$on('media_archive', refreshItems);
        $scope.$on('item:fetch', refreshItems);
        $scope.$on('item:copy', refreshItems);
        $scope.$on('item:take', refreshItems);
        $scope.$on('item:duplicate', refreshItems);
        $scope.$on('content:update', refreshItems);
        $scope.$on('content:expired', refreshItems);
        $scope.$on('item:deleted', refreshItems);
        $scope.$on('item:highlight', refreshItems);
        $scope.$on('item:spike', reset);
        $scope.$on('item:unspike', reset);

        desks.fetchCurrentUserDesks().then(function() {
            // only watch desk/stage after we get current user desk
            $scope.$watch(function() {
                return desks.active;
            }, function(active) {
                $scope.selected = active;
                if ($location.search().page) {
                    $location.search('page', null);
                    return; // will reload via $routeUpdate
                }

                refreshItems();
            });
        });

        // reload on route change if there is still the same _id
        var oldQuery = _.omit($location.search(), '_id', 'fetch');
        $scope.$on('$routeUpdate', function(e, route) {
            var query = _.omit($location.search(), '_id', 'fetch');
            if (!angular.equals(oldQuery, query)) {
                refreshItems();
            }
            oldQuery = query;
        });
    }]);
})();
