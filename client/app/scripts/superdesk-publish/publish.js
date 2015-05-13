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

    PublishQueueController.$inject = ['$scope', 'adminPublishSettingsService', 'api', '$q', 'notify'];
    function PublishQueueController($scope, adminPublishSettingsService, api, $q, notify) {
        $scope.subscribers = null;
        $scope.subscriberLookup = {};
        $scope.outputChannels = null;
        $scope.outputChannelLookup = {};
        $scope.formattedItems = null;
        $scope.formattedItemLookup = {};
        $scope.publish_queue = null;

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

        promises.push(adminPublishSettingsService.fetchFormattedItems().then(function(items) {
            $scope.formattedItems = items._items;
            _.each(items._items, function(item) {
                $scope.formattedItemLookup[item._id] = item;
            });
        }));

        function fetchPublishQueue () {
            var criteria = criteria || {};
            criteria.max_results = 200;
            criteria.sort = '[(\'_created\',-1)]';
            return api.publish_queue.query(criteria);
        }

        $scope.reload = function() {
            $q.all(promises).then(function() {
                fetchPublishQueue().then(function(queue) {
                    $scope.publish_queue = queue._items;
                    $scope.lastRefreshedAt = new Date();
                });
            });
        };

        $scope.scheduleToSend = function(item) {
            var newItem = {};

            newItem.publishing_action = item.publishing_action;
            newItem.item_id = item.item_id;
            newItem.published_seq_num = item.published_seq_num;
            newItem.publish_schedule = item.publish_schedule;
            newItem.selector_codes = item.selector_codes;
            newItem.formatted_item_id = item.formatted_item_id;
            newItem.headline = item.headline;
            newItem.content_type = item.content_type;
            newItem.subscriber_id = item.subscriber_id;
            newItem.output_channel_id = item.output_channel_id;
            newItem.unique_name = item.unique_name;
            newItem.destination = item.destination;

            api.publish_queue.save({}, newItem).then(
                function(response) {
                    $scope.reload();
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

        $scope.cancelSchedule = function(item) {
            api.publish_queue.save(item, {'state': 'canceled', 'error_message': 'canceled by user'}).then(
                function(response) {
                    $scope.reload();
                },
                function(response) {
                    if (angular.isDefined(response.data._issues)) {
                        if (angular.isDefined(response.data._issues['validator exception'])) {
                            notify.error(gettext('Error: ' + response.data._issues['validator exception']));
                        }
                    } else {
                        notify.error(gettext('Error: Failed to cancel the schedule'));
                    }
                }
            );
        };

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
        .directive('sdDestination', DestinationDirective);

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
