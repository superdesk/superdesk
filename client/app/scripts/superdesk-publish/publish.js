/**
 * This file is part of Superdesk.
 *
 * Copyright 2013, 2014 Sourcefabric z.u. and contributors.
 *
 * For the full copyright and license information, please see the
 * AUTHORS and LICENSE files distributed with this source code, or
 * at https://www.sourcefabric.org/superdesk/license
 */

(function() {
    'use strict';

    var app = angular.module('superdesk.publish', ['superdesk.users', 'superdesk.publish.filters']);

    app.value('transmissionTypes', {
        ftp: {
            label: 'FTP',
            templateUrl: 'scripts/superdesk-publish/views/ftp-config.html'
        },
        email: {
            label: 'Email',
            templateUrl: 'scripts/superdesk-publish/views/email-config.html'
        },
        ODBC: {
            label: 'ODBC',
            templateUrl: 'scripts/superdesk-publish/views/odbc-config.html'
        },
        File: {
            label: 'File',
            templateUrl: 'scripts/superdesk-publish/views/file-config.html'
        },
        pull: {
            label: 'Pull'
        },
        PublicArchive: {
            label: 'Public Archive',
            templateUrl: 'scripts/superdesk-publish/views/public-archive-config.html'
        }
    });

    AdminPublishSettingsController.$inject = ['$scope', 'privileges'];
    function AdminPublishSettingsController($scope, privileges) {
        var user_privileges = privileges.privileges;

        $scope.showSubscribers  = Boolean(user_privileges.subscribers);
        $scope.showFilterConditions  = Boolean(user_privileges.publish_filters);
    }

    AdminPublishSettingsService.$inject = ['api', '$q'];
    function AdminPublishSettingsService(api, $q) {
        var _fetch = function(endpoint, criteria) {
            return api[endpoint].query(criteria);
        };

        var service = {
            fetchSubscribers: function(criteria) {
                criteria = criteria || {};
                return _fetch('subscribers', criteria);
            },

            fetchSubscribersByKeyword: function(keyword) {
                return this.fetchSubscribers({
                    where: JSON.stringify({
                        '$or': [
                            {name: {'$regex': keyword, '$options': '-i'}}
                        ]
                    })
                });
            },

            fetchSubscribersByIds: function(ids) {
                var parts = [];
                _.each(ids, function(id) {
                    parts.push({_id: id});
                });
                return this.fetchSubscribers({
                    where: JSON.stringify({'$or': parts})
                });
            },

            fetchPublishErrors: function() {
                var criteria = {'io_type': 'publish'};
                return _fetch('io_errors', criteria);
            }
        };

        return service;
    }

    DestinationDirective.$inject = ['transmissionTypes'];
    function DestinationDirective(transmissionTypes) {
        return {
            templateUrl: 'scripts/superdesk-publish/views/destination.html',
            scope: {
                destination: '=',
                actions: '='
            },
            link: function ($scope) {
                $scope.types = transmissionTypes;
            }
        };
    }

    DataConsistencyController.$inject = ['$scope', 'api'];
    function DataConsistencyController($scope, api) {
        $scope.consistency_records = null;

        function fetchConsistencyRecords () {
            var criteria = criteria || {};
            criteria.max_results = 200;
            return api.consistency.query(criteria);
        }

        $scope.reload = function() {
            fetchConsistencyRecords().then(function(data) {
                $scope.consistency_records = data._items;
                $scope.lastRefreshedAt = new Date();
            });
        };

        $scope.reload ();
    }

    PublishQueueController.$inject = ['$scope', 'adminPublishSettingsService', 'api', '$q', 'notify', '$location'];
    function PublishQueueController($scope, adminPublishSettingsService, api, $q, notify, $location) {
        $scope.subscribers = null;
        $scope.subscriberLookup = {};
        $scope.publish_queue = [];
        $scope.selectedFilterSubscriber = null;
        $scope.multiSelectCount = 0;
        $scope.selectedQueueItems = [];
        $scope.showResendBtn = false;
        $scope.showCancelBtn = false;
        $scope.selected = {};

        var promises = [];

        promises.push(adminPublishSettingsService.fetchSubscribers().then(function(items) {
            $scope.subscribers = items._items;
            _.each(items._items, function(item) {
                $scope.subscriberLookup[item._id] = item;
            });
        }));

        function fetchPublishQueue () {
            var criteria = criteria || {};
            criteria.max_results = 200;
            criteria.sort = '[(\'published_seq_num\',-1)]';

            if ($scope.selectedFilterSubscriber !== null) {
                criteria.where = {'subscriber_id': $scope.selectedFilterSubscriber._id};
            }

            return api.publish_queue.query(criteria);
        }

        $scope.reload = function() {
            $q.all(promises).then(function() {
                fetchPublishQueue().then(function(queue) {
                    var queuedItems = queue._items;

                    _.forEach(queuedItems, function(item) {
                        angular.extend(item, {'selected': false});
                    });

                    $scope.publish_queue = queuedItems;
                    $scope.lastRefreshedAt = new Date();
                    $scope.showResendBtn = false;
                    $scope.showCacnelBtn = false;

                    previewItem();
                });
            });
        };

        $scope.buildNewSchedule = function (item) {
            var pick_fields = ['item_id', 'item_version', 'publishing_action', 'formatted_item', 'headline',
                'content_type', 'subscriber_id', 'unique_name', 'destination'];

            var newItem = _.pick(item, pick_fields);
            return newItem;
        };

        $scope.scheduleToSend = function(item) {
            var queueItems = [];

            if (angular.isDefined(item)) {
                queueItems.push($scope.buildNewSchedule(item));
            } else if ($scope.multiSelectCount > 0) {
                _.forEach($scope.selectedQueueItems, function(item) {
                    queueItems.push($scope.buildNewSchedule(item));
                });
            }

            api.publish_queue.save([], queueItems).then(
                function(response) {
                    $scope.reload();
                    $scope.cancelSelection();
                },
                function(response) {
                    if (angular.isDefined(response.data._issues)) {
                        if (angular.isDefined(response.data._issues['validator exception'])) {
                            notify.error(gettext('Error: ' + response.data._issues['validator exception']));
                        }
                    } else {
                        notify.error(gettext('Error: Failed to re-schedule'));
                    }
                }
            );
        };

        $scope.filterSchedule = function(item, type) {
            if (type === 'subscriber') {
                $scope.selectedFilterSubscriber = item;
            }

            $scope.multiSelectCount = 0;
            fetchPublishQueue().then(function(queue) {
                var queuedItems = queue._items;

                _.forEach(queuedItems, function(item) {
                    angular.extend(item, {'selected': false});
                });

                $scope.publish_queue = queuedItems;
                $scope.lastRefreshedAt = new Date();
                $scope.showResendBtn = false;
                $scope.showCancelBtn = false;
                $scope.selectedQueueItems = [];
            });
        };

        $scope.selectQueuedItem = function(queuedItem) {
            if (queuedItem.selected) {
                $scope.selectedQueueItems = _.union($scope.selectedQueueItems, [queuedItem]);
            } else {
                $scope.selectedQueueItems = _.without($scope.selectedQueueItems, queuedItem);
            }

            var idx = _.findIndex($scope.selectedQueueItems, function(item) {
                return item.state === 'pending' || item.state === 'in-progress' || item.state === 'canceled';
            });

            if (idx === -1) {
                $scope.showResendBtn = true;
                $scope.showCancelBtn = false;
            } else {
                idx = _.findIndex($scope.selectedQueueItems, function(item) {
                    return item.state === 'success' || item.state === 'in-progress' || item.state === 'canceled' ||
                        item.state === 'error';
                });

                if (idx === -1) {
                    $scope.showResendBtn = false;
                    $scope.showCancelBtn = true;
                } else {
                    $scope.showResendBtn = false;
                    $scope.showCancelBtn = false;
                }
            }

            $scope.multiSelectCount = $scope.selectedQueueItems.length;
        };

        $scope.cancelSelection = function() {
            $scope.selectedFilterSubscriber = null;
            $scope.selectedQueueItems = [];
            $scope.multiSelectCount = 0;
            $scope.filterSchedule();
        };

        function refreshQueueState (data) {
            var item = _.find($scope.publish_queue, {'_id': data.queue_id});

            if (item) {
                var fields = ['error_message', 'completed_at', 'state'];
                angular.extend(item, _.pick(data, fields));
                $scope.$apply();
            }
        }

        $scope.preview = function(queueItem) {
            $location.search('_id', queueItem ? queueItem._id : queueItem);
        };

        function previewItem() {
            var queueItem = _.find($scope.publish_queue, {_id: $location.search()._id}) || null;
            if (queueItem) {
                api.archive.getById(queueItem.item_id)
                .then(function(item) {
                    $scope.selected.preview = item;
                });
            } else {
                $scope.selected.preview = null;
            }
        }

        $scope.$on('$routeUpdate', previewItem);

        $scope.$on('publish_queue:update', function(evt, data) { refreshQueueState(data); });
        $scope.reload();
    }

    SubscribersDirective.$inject = ['gettext', 'notify', 'api', 'adminPublishSettingsService', 'modal', 'metadata', 'filters', '$q'];
    function SubscribersDirective(gettext, notify, api, adminPublishSettingsService, modal, metadata, filters, $q) {
        return {
            templateUrl: 'scripts/superdesk-publish/views/subscribers.html',
            link: function ($scope) {
                $scope.subscriber = null;
                $scope.origSubscriber = null;
                $scope.subscribers = null;
                $scope.newDestination = null;
                $scope.publishFilters = null;
                $scope.geoRestrictions = null;
                $scope.subTypes = null;

                if (angular.isDefined(metadata.values.geographical_restrictions)) {
                    $scope.geoRestrictions = metadata.values.geographical_restrictions;
                    $scope.subTypes = metadata.values.subscriber_types;
                } else {
                    metadata.fetchMetadataValues().then(function() {
                        $scope.geoRestrictions = metadata.values.geographical_restrictions;
                        $scope.subTypes = metadata.values.subscriber_types;
                    });
                }

                function fetchSubscribers() {
                    adminPublishSettingsService.fetchSubscribers().then(
                        function(result) {
                            $scope.subscribers = result;
                        }
                    );
                }

                var fetchPublishFilters = function() {
                    return api.query('publish_filters').then(function(filters) {
                        $scope.publishFilters = filters._items;
                    });
                };

                var initGlobalFilters = function() {
                    if (!$scope.subscriber) {
                        return;
                    }

                    if (!$scope.subscriber.global_filters) {
                        $scope.subscriber.global_filters = {};
                    }

                    _.each($scope.globalFilters, function(filter) {
                        if (!(filter._id in $scope.subscriber.global_filters)) {
                            $scope.subscriber.global_filters[filter._id] = true;
                        }
                    });
                };

                var fetchGlobalPublishFilters = function() {
                    return filters.getGlobalPublishFilters().then(function(filters) {
                        $scope.globalFilters = filters;
                    });
                };

                function fetchPublishErrors() {
                    return adminPublishSettingsService.fetchPublishErrors().then(function(result) {
                        $scope.all_errors = result._items[0].all_errors;
                    });
                }

                $scope.addNewDestination = function() {
                    $scope.newDestination = {};
                };

                $scope.cancelNewDestination = function() {
                    $scope.newDestination = null;
                };

                $scope.saveNewDestination = function() {
                    $scope.subscriber.destinations.push($scope.newDestination);
                    $scope.newDestination = null;
                };

                $scope.deleteDestination = function(destination) {
                    _.remove($scope.subscriber.destinations, destination);
                };

                $scope.save = function() {

                    if ($scope.subscriber.publish_filter && $scope.subscriber.publish_filter.filter_id === '') {
                        $scope.subscriber.publish_filter = null;
                    }

                    api.subscribers.save($scope.origSubscriber, $scope.subscriber)
                        .then(
                            function() {
                                notify.success(gettext('Subscriber saved.'));
                                $scope.cancel();
                            },
                            function(response) {
                                if (angular.isDefined(response.data._issues)) {
                                    if (angular.isDefined(response.data._issues['validator exception'])) {
                                        notify.error(gettext('Error: ' + response.data._issues['validator exception']));
                                    } else if (angular.isDefined(response.data._issues.name) &&
                                        angular.isDefined(response.data._issues.name.unique)) {
                                        notify.error(gettext('Error: Subscriber with Name ' + $scope.subscriber.name +
                                            ' already exists.'));
                                    } else if (angular.isDefined(response.data._issues.destinations)) {
                                        notify.error(gettext('Error: Subscriber must have at least one destination.'));
                                    }
                                } else {
                                    notify.error(gettext('Error: Failed to save Subscriber.'));
                                }
                            }
                        ).then(fetchSubscribers);
                };

                $scope.edit = function(subscriber) {
                    var promises = [];
                    promises.push(fetchPublishErrors());
                    promises.push(fetchPublishFilters());
                    promises.push(fetchGlobalPublishFilters());

                    $q.all(promises).then(function() {
                        $scope.origSubscriber = subscriber || {};
                        $scope.subscriber = _.create($scope.origSubscriber);
                        $scope.subscriber.critical_errors = $scope.origSubscriber.critical_errors;
                        $scope.subscriber.publish_filter = $scope.origSubscriber.publish_filter || {};
                        $scope.subscriber.destinations = $scope.subscriber.destinations || [];
                        $scope.subscriber.global_filters =  $scope.origSubscriber.global_filters || {};
                        $scope.subscriber.publish_filter.filter_type = $scope.subscriber.publish_filter.filter_type  || 'blocking';
                        initGlobalFilters();
                    }, function() {
                        notify.error(gettext('Subscriber could not be initialized!'));
                    });
                };

                $scope.remove = function(subscriber) {
                    modal.confirm(gettext('Are you sure you want to delete subscriber?'))
                    .then(function() {
                        return api.subscribers.remove(subscriber);
                    })
                    .then(function(result) {
                        _.remove($scope.subscribers, subscriber);
                    }, function(response) {
                        if (angular.isDefined(response.data._message)) {
                            notify.error(gettext('Error: ' + response.data._message));
                        } else {
                            notify.error(gettext('There is an error. Subscriber cannot be deleted.'));
                        }
                    })
                    .then(fetchSubscribers);
                };

                $scope.cancel = function() {
                    $scope.origSubscriber = null;
                    $scope.subscriber = null;
                    $scope.newDestination = null;
                };

                fetchSubscribers();
            }
        };
    }

    app
        .service('adminPublishSettingsService', AdminPublishSettingsService)
        .directive('sdAdminPubSubscribers', SubscribersDirective)
        .directive('sdDestination', DestinationDirective)
        .controller('publishQueueCtrl', PublishQueueController);

    app
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/settings/publish', {
                    label: gettext('Publish'),
                    templateUrl: 'scripts/superdesk-publish/views/settings.html',
                    controller: AdminPublishSettingsController,
                    category: superdesk.MENU_SETTINGS,
                    privileges: {subscribers: 1},
                    priority: 2000,
                    beta: true
                })
                .activity('/publish_queue', {
                    label: gettext('Publish Queue'),
                    templateUrl: 'scripts/superdesk-publish/views/publish-queue.html',
                    controller: PublishQueueController,
                    category: superdesk.MENU_MAIN,
                    privileges: {publish_queue: 1}
                })
                .activity('/settings/data_consistency', {
                    label: gettext('Data Consistency'),
                    templateUrl: 'scripts/superdesk-publish/views/data-consistency.html',
                    controller: DataConsistencyController,
                    category: superdesk.MENU_SETTINGS,
                    privileges: {subscribers: 1},
                    priority: 2000,
                    beta: true
                });
        }])
        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('subscribers', {
                type: 'http',
                backend: {
                    rel: 'subscribers'
                }
            });
            apiProvider.api('publish_queue', {
                type: 'http',
                backend: {
                    rel: 'publish_queue'
                }
            });
            apiProvider.api('consistency', {
                type: 'http',
                backend: {
                    rel: 'consistency'
                }
            });
            apiProvider.api('formatted_item', {
                type: 'http',
                backend: {
                    rel: 'formatted_item'
                }
            });
            apiProvider.api('io_errors', {
                type: 'http',
                backend: {
                    rel: 'io_errors'
                }
            });
            apiProvider.api('publish_filters', {
                type: 'http',
                backend: {
                    rel: 'publish_filters'
                }
            });
            apiProvider.api('publish_filter_test', {
                type: 'http',
                backend: {
                    rel: 'publish_filter_test'
                }
            });
        }]);

    return app;
})();
