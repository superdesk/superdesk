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
        this.isSelected = function isSelected(item) {
            return !!_.find(items, {_id: item._id});
        };

        /**
         * Toggle item selected state
         *
         * @param {Object} item
         */
        this.toggle = function toggle(item) {
            item.selected = !this.isSelected(item);
            if (item.selected) {
                items = _.union(items, [item]);
            } else {
                items = _.without(items, item);
            }
            this.count = items.length;
        };

        /**
         * Get list of selected items
         */
        this.getQueue = function getQueue() {
            return _.map(items, '_id');
        };

        /**
         * Reset to empty
         */
        this.reset = function reset() {
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
        this.spike = function spike(item) {
            return api.update(SPIKE_RESOURCE, item, {state: 'spiked'})
                .then(function() {
                    if ($location.search()._id === item._id) {
                        $location.search('_id', null);
                    }
                }, function(response) {
                    item.error = response;
                })
                ['finally'](function() {
                    item.actioning.spike = false;
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
    }

    ListLayoutController.$inject = ['preferences'];
    function ListLayoutController(preferences) {
        var MAX_VIEW = Object.freeze({max: true}),
            MIN_VIEW = Object.freeze({min: true}),
            ITEM_VIEW = Object.freeze({extended: true}),
            COMPACT_VIEW = Object.freeze({compact: true});

        this.view = MAX_VIEW;

        this.openItem = openItem;
        this.closeItem = closeItem;
        this.closeList = closeList;
        this.openList = openList;
        this.closeEditor = closeEditor;
        this.compactView = toggleCompactView;
        this.extendedView = toggleExtendedView;

        var vm = this,
            listView;

        return activate();

        function activate() {
            preferences.get('list:view').then(function(listPreferences) {
                listView = listPreferences && listPreferences.view === 'compact' ? COMPACT_VIEW : ITEM_VIEW;
            });
        }

        function openItem(item) {
            vm.item = item;
            openList();
        }

        function closeItem() {
            vm.item = null;
            closeEditor();
        }

        function closeList() {
            vm.view = MIN_VIEW;
        }

        function openList() {
            vm.view = listView;
        }

        function closeEditor() {
            vm.view = MAX_VIEW;
        }

        function toggleCompactView() {
            vm.view = listView = COMPACT_VIEW;
            savePreferences();
        }

        function toggleExtendedView() {
            vm.view = listView = ITEM_VIEW;
            savePreferences();
        }

        function savePreferences() {
            var view = Object.keys(vm.view)[0];
            preferences.update({'list:view': {view: view}}, 'list:view');
        }
    }

    function ListLayoutDirective() {
        return {
            controller: 'ListLayout',
            controllerAs: 'layout'
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

        .controller('ListLayout', ListLayoutController)

        .directive('sdListLayout', ListLayoutDirective)

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
                    icon: 'revert',
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
                .activity('duplicate-content', {
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
                .activity('copy-content', {
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
                .activity('New Take', {
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
                .activity('Re-write', {
                    label: gettext('Re-write'),
                    icon: 'multi-star-color',
                    filters: [{action: 'list', type: 'archive'}],
                    privileges: {archive: 1},
                    condition: function(item) {
                        return (item.lock_user === null || angular.isUndefined(item.lock_user));
                    },
                    additionalCondition:['authoring', 'item', function(authoring, item) {
                        return authoring.itemActions(item).re_write;
                    }],
                    controller: ['data', '$location', 'api', 'notify', 'session', 'desks', 'superdesk',
                        function(data, $location, api, notify, session, desks, superdesk) {
                            var pick_fields = ['family_id', 'abstract', 'anpa-category',
                                                'pubstatus', 'destination_groups',
                                                'slugline', 'urgency', 'subject', 'dateline',
                                                'priority', 'byline', 'dateline', 'headline'];
                            var update_item = {};
                            update_item =  _.pick(angular.extend(update_item, data.item), pick_fields);
                            update_item.related_to = data.item._id;
                            update_item.anpa_take_key = 'update';
                            update_item.task = {};

                            session.getIdentity()
                                .then(function(user) {
                                    update_item.task.desk = user.desk? user.desk: desks.getCurrentDeskId();
                                    update_item.state = 'in_progress';
                                    return api.archive.save({}, update_item);
                                })
                                .then(function(new_item) {
                                    notify.success(gettext('Update Created.'));
                                    superdesk.intent('author', 'article', new_item);
                                }, function(response) {
                                    notify.error(gettext('Failed to generate update.'));
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
        }]);
});
