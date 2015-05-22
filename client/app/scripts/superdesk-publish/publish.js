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

    var app = angular.module('superdesk.publish', ['superdesk.users']);

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
        }
    });

    AdminPublishSettingsController.$inject = ['$scope', 'privileges'];
    function AdminPublishSettingsController($scope, privileges) {
        var user_privileges = privileges.privileges;

        $scope.showOutputChannels   = Boolean(user_privileges.output_channels);
        $scope.showDestinationGroups  = Boolean(user_privileges.destination_groups);
        $scope.showSubscribers  = Boolean(user_privileges.subscribers);
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

            fetchOutputChannels: function(criteria) {
                criteria = criteria || {};
                criteria.max_results = 200;
                return _fetch('output_channels', criteria);
            },

            fetchOutputChannelsByKeyword: function(keyword) {
                return this.fetchOutputChannels({
                    where: JSON.stringify({
                        '$or': [
                            {name: {'$regex': keyword, '$options': '-i'}}
                        ]
                    })
                });
            },

            fetchOutputChannelsByIds: function(ids) {
                var parts = [];
                _.each(ids, function(id) {
                    parts.push({_id: id});
                });
                return this.fetchOutputChannels({
                    where: JSON.stringify({'$or': parts})
                });
            },

            fetchFormattedItems: function(criteria) {
                criteria = criteria || {};
                criteria.max_results = 200;
                return _fetch('formatted_item', criteria);
            },

            fetchDestinationGroups: function(criteria) {
                criteria = criteria || {};
                criteria.max_results = 200;
                return _fetch('destination_groups', criteria);
            },

            fetchDestinationGroupsByKeyword: function(keyword) {
                return this.fetchDestinationGroups({
                    where: JSON.stringify({
                        '$or': [
                            {name: {'$regex': keyword, '$options': '-i'}}
                        ]
                    })
                });
            },

            fetchDestinationGroupsByIds: function(ids) {
                var parts = [];
                _.each(ids, function(id) {
                    parts.push({_id: id});
                });
                return this.fetchDestinationGroups({
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

    PublishQueueController.$inject = ['$scope', 'adminPublishSettingsService', 'api', '$q', 'notify'];
    function PublishQueueController($scope, adminPublishSettingsService, api, $q, notify) {
        $scope.subscribers = null;
        $scope.subscriberLookup = {};
        $scope.outputChannels = null;
        $scope.outputChannelLookup = {};
        $scope.publish_queue = [];
        $scope.selectedFilterChannel = null;
        $scope.selectedFilterSubscriber = null;
        $scope.multiSelectCount = 0;
        $scope.selectedQueueItems = [];
        $scope.showResendBtn = false;
        $scope.showCancelBtn = false;

        var promises = [];

        promises.push(adminPublishSettingsService.fetchSubscribers().then(function(items) {
            $scope.subscribers = items._items;
            _.each(items._items, function(item) {
                $scope.subscriberLookup[item._id] = item;
            });
        }));

        promises.push(adminPublishSettingsService.fetchOutputChannels().then(function(items) {
            $scope.outputChannels = items._items;
            _.each(items._items, function(item) {
                $scope.outputChannelLookup[item._id] = item;
            });
        }));

        function fetchPublishQueue () {
            var criteria = criteria || {};
            criteria.max_results = 200;
            criteria.sort = '[(\'published_seq_num\',-1)]';

            if ($scope.selectedFilterSubscriber !== null && $scope.selectedFilterChannel !== null) {
                criteria.where = JSON.stringify({
                        '$and': [
                            {'output_channel_id': $scope.selectedFilterChannel._id},
                            {'subscriber_id': $scope.selectedFilterSubscriber._id}
                        ]
                    });
            } else if ($scope.selectedFilterChannel !== null) {
                criteria.where = {'output_channel_id': $scope.selectedFilterChannel._id};
            } else if ($scope.selectedFilterSubscriber !== null) {
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
                });
            });
        };

        $scope.buildNewSchedule = function (item) {
            var pick_fields = ['item_id', 'publishing_action', 'selector_codes',
                'formatted_item_id', 'headline', 'content_type',
                'subscriber_id', 'output_channel_id', 'unique_name', 'destination'];

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

        $scope.filterSchedule = function() {
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
            $scope.selectedFilterChannel = null;
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

        $scope.$on('publish_queue:update', function(evt, data) { refreshQueueState(data); });
        $scope.reload();
    }

    SubscribersDirective.$inject = ['gettext', 'notify', 'api', 'adminPublishSettingsService', 'modal'];
    function SubscribersDirective(gettext, notify, api, adminPublishSettingsService, modal) {
        return {
            templateUrl: 'scripts/superdesk-publish/views/subscribers.html',
            link: function ($scope) {
                $scope.subscriber = null;
                $scope.origSubscriber = null;
                $scope.subscribers = null;
                $scope.newDestination = null;

                function fetchSubscribers() {
                    adminPublishSettingsService.fetchSubscribers().then(
                        function(result) {
                            $scope.subscribers = result;
                        }
                    );
                }

                function fetchPublishErrors() {
                    adminPublishSettingsService.fetchPublishErrors().then(function(result) {
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
                    $scope.subscriber.destinations = $scope.subscriber.destinations || [];
                    $scope.subscriber.destinations.push($scope.newDestination);
                    $scope.newDestination = null;
                };

                $scope.deleteDestination = function(destination) {
                    _.remove($scope.subscriber.destinations, destination);
                };

                $scope.save = function() {
                    $scope.subscriber.destinations = $scope.subscriber.destinations;
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
                                    }
                                } else {
                                    notify.error(gettext('Error: Failed to save Subscriber.'));
                                }
                            }
                        ).then(fetchSubscribers);
                };

                $scope.edit = function(subscriber) {
                    $scope.origSubscriber = subscriber || {};
                    $scope.subscriber = _.create($scope.origSubscriber);
                    $scope.subscriber.critical_errors = $scope.origSubscriber.critical_errors;
                    if (subscriber) {
                        fetchPublishErrors();
                    }
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

    OutputChannelsDirective.$inject = ['gettext', 'notify', 'api', 'adminPublishSettingsService', 'modal', 'privileges'];
    function OutputChannelsDirective(gettext, notify, api, adminPublishSettingsService, modal, privileges) {
        return {
            templateUrl: 'scripts/superdesk-publish/views/output-channels.html',
            link: function ($scope) {
                $scope.outputChannel = null;
                $scope.origOutputChannel = null;
                $scope.outputChannels = null;
                $scope.subscribers = null;
                $scope.subscriberLookup = {};
                $scope.newSubscriber = {_id: null};
                $scope.can_update_seq_num_settings = Boolean(privileges.privileges.output_channel_seq_num_settings);

                function fetchOutputChannels() {
                    adminPublishSettingsService.fetchOutputChannels().then(
                        function(result) {
                            $scope.outputChannels = result;
                        }
                    );
                }

                function fetchSubscribers() {
                    adminPublishSettingsService.fetchSubscribers().then(
                        function(result) {
                            $scope.subscribers = result;
                            _.each(result._items, function(item) {
                                $scope.subscriberLookup[item._id] = item;
                            });
                        }
                    );
                }

                function fetchPublishErrors() {
                    adminPublishSettingsService.fetchPublishErrors().then(function(result) {
                        $scope.all_errors = result._items[0].all_errors;
                    });
                }

                $scope.isIncluded = function(subscriber) {
                    return $scope.outputChannel.destinations && $scope.outputChannel.destinations.indexOf(subscriber._id) !== -1;
                };

                $scope.addNewSubscriber = function() {
                    $scope.newSubscriber._id = true;
                };

                $scope.saveNewSubscriber = function() {
                    $scope.outputChannel.destinations = $scope.outputChannel.destinations || [];
                    $scope.outputChannel.destinations.push($scope.newSubscriber._id);
                    $scope.newSubscriber._id = null;
                };

                $scope.cancelNewSubscriber = function() {
                    $scope.newSubscriber._id = null;
                };

                $scope.removeSubscriber = function(subscriberId) {
                    $scope.outputChannel.destinations = _.without($scope.outputChannel.destinations, subscriberId);
                };

                $scope.save = function() {
                    api.output_channels.save($scope.origOutputChannel, $scope.outputChannel)
                        .then(
                            function() {
                                notify.success(gettext('Output Channel saved.'));
                                $scope.cancel();
                            },
                            function(response) {
                                if (angular.isDefined(response.data._issues)) {
                                    if (angular.isDefined(response.data._message)) {
                                        notify.error(gettext('Error: ' + response.data._message));
                                    } else if (angular.isDefined(response.data._issues['validator exception'])) {
                                        notify.error(gettext('Error: ' + response.data._issues['validator exception']));
                                    }
                                } else {
                                    notify.error(gettext('Error: Failed to save Output Channel.'));
                                }
                            }
                        ).then(fetchOutputChannels);
                };

                $scope.edit = function(outputChannel) {
                    $scope.origOutputChannel = outputChannel || {};

                    $scope.outputChannel = _.create($scope.origOutputChannel);
                    $scope.outputChannel.sequence_num_settings = $scope.origOutputChannel.sequence_num_settings || {};
                    $scope.outputChannel.critical_errors = $scope.origOutputChannel.critical_errors;

                    if (outputChannel) {
                        fetchPublishErrors();
                    }
                };

                $scope.remove = function(outputChannel) {
                    modal.confirm(gettext('Are you sure you want to delete output channel?'))
                    .then(function() {
                        return api.output_channels.remove(outputChannel);
                    })
                    .then(function(result) {
                        _.remove($scope.outputChannels, outputChannel);
                    }, function(response) {
                        if (angular.isDefined(response.data._message)) {
                            notify.error(gettext('Error: ' + response.data._message));
                        } else {
                            notify.error(gettext('There is an error. Output Channel cannot be deleted.'));
                        }
                    })
                    .then(fetchOutputChannels);
                };

                $scope.cancel = function() {
                    $scope.origOutputChannel = null;
                    $scope.outputChannel = null;
                };

                fetchOutputChannels();
                fetchSubscribers();
            }
        };
    }

    DestinationGroupsDirective.$inject = ['gettext', 'notify', 'api', 'adminPublishSettingsService', 'modal'];
    function DestinationGroupsDirective(gettext, notify, api, adminPublishSettingsService, modal) {
        return {
            templateUrl: 'scripts/superdesk-publish/views/destination-groups.html',
            link: function ($scope) {
                $scope.destinationGroups = null;
                $scope.origDestinationGroup = null;
                $scope.destinationGroup = null;
                $scope.selectedDestinationGroups = null;
                $scope.selectedOutputChannels = null;

                $scope.selectorData = {
                    add: function(channel, code) {
                        if (code) {
                            this.codes[channel] = this.codes[channel] || [];
                            this.codes[channel].push(code);
                        }
                    },
                    remove: function(channel, code) {
                        _.remove(this.codes[channel], function(c) {
                            return c === code;
                        });
                    },
                    codes: null
                };

                $scope.edit = function(destinationGroup) {
                    $scope.origDestinationGroup = destinationGroup || {};
                    $scope.destinationGroup = _.create($scope.origDestinationGroup);
                    $scope.selectedDestinationGroups = [];
                    $scope.selectedOutputChannels = [];
                    $scope.selectorData.codes = {};
                    var destinationGroupIds = [];
                    _.each($scope.destinationGroup.destination_groups, function(item) {
                        destinationGroupIds.push(item);
                    });
                    if (destinationGroupIds.length) {
                        adminPublishSettingsService.fetchDestinationGroupsByIds(destinationGroupIds)
                        .then(function(result) {
                            $scope.selectedDestinationGroups = result._items;
                        });
                    }
                    var outputChannelIds = [];
                    _.each($scope.destinationGroup.output_channels, function(item) {
                        outputChannelIds.push(item.channel);
                        $scope.selectorData.codes[item.channel] = item.selector_codes;
                    });
                    if (outputChannelIds.length) {
                        adminPublishSettingsService.fetchOutputChannelsByIds(outputChannelIds)
                        .then(function(result) {
                            $scope.selectedOutputChannels = result._items;
                        });
                    }
                };

                $scope.cancel = function() {
                    $scope.origDestinationGroup = null;
                    $scope.destinationGroup = null;
                    $scope.selectedDestinationGroups = null;
                    $scope.selectedOutputChannels = null;
                    $scope.selectorData.codes = null;
                };

                $scope.save = function() {
                    $scope.destinationGroup.destination_groups = [];
                    _.each($scope.selectedDestinationGroups, function(group) {
                        $scope.destinationGroup.destination_groups.push(group._id);
                    });
                    $scope.destinationGroup.output_channels = [];
                    _.each($scope.selectedOutputChannels, function(channel) {
                        var outputChannel = {
                            channel: channel._id
                        };
                        if ($scope.selectorData.codes[channel._id]) {
                            outputChannel.selector_codes = $scope.selectorData.codes[channel._id];
                        }
                        $scope.destinationGroup.output_channels.push(outputChannel);
                    });
                    api.destination_groups.save($scope.origDestinationGroup, $scope.destinationGroup)
                    .then(function() {
                        notify.success(gettext('Destination Group saved.'));
                        $scope.cancel();
                    }, function(response) {
                        if (angular.isDefined(response.data._issues) &&
                                angular.isDefined(response.data._issues['validator exception'])) {
                            notify.error(gettext('Error: ' + response.data._issues['validator exception']));
                        } else {
                            notify.error(gettext('Error: Failed to save Destination Group.'));
                        }
                    })
                    ['finally'](function() {
                        fetchDestinationGroups();
                    });
                };

                $scope.remove = function(destinationGroup) {
                    modal.confirm(gettext('Are you sure you want to delete destination group?'))
                    .then(function() {
                        return api.destination_groups.remove(destinationGroup);
                    })
                    .then(function(result) {
                        _.remove($scope.destinationGroups._items, destinationGroup);
                    }, function(response) {
                        if (angular.isDefined(response.data._message)) {
                            notify.error(gettext('Error: ' + response.data._message));
                        } else {
                            notify.error(gettext('There is an error. Destination Group cannot be deleted.'));
                        }
                    })
                    .then(fetchDestinationGroups);
                };

                function fetchDestinationGroups() {
                    return adminPublishSettingsService.fetchDestinationGroups()
                    .then(function(result) {
                        $scope.destinationGroups = result;
                        return result;
                    });
                }

                fetchDestinationGroups();
            }
        };
    }

    app
        .service('adminPublishSettingsService', AdminPublishSettingsService)
        .directive('sdAdminPubSubscribers', SubscribersDirective)
        .directive('sdAdminPubOutputChannels', OutputChannelsDirective)
        .directive('sdAdminPubDestinationGroups', DestinationGroupsDirective)
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
                    privileges: {output_channels: 1, destination_groups: 1, subscribers: 1},
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
                    privileges: {output_channels: 1, destination_groups: 1, subscribers: 1},
                    priority: 2000,
                    beta: true
                });
        }])
        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('output_channels', {
                type: 'http',
                backend: {
                    rel: 'output_channels'
                }
            });
            apiProvider.api('destination_groups', {
                type: 'http',
                backend: {
                    rel: 'destination_groups'
                }
            });
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
        }]);

    return app;
})();
