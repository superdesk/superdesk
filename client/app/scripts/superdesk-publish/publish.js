(function() {
    'use strict';

    var app = angular.module('superdesk.publish', ['superdesk.users']);

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
            }
        };

        return service;
    }

    DestinationDirective.$inject = [];
    function DestinationDirective() {
        return {
            templateUrl: 'scripts/superdesk-publish/views/destination.html',
            scope: {
                destination: '=',
                actions: '='
            },
            link: function ($scope) {
            }
        };
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
                                if (angular.isDefined(response.data._issues) &&
                                        angular.isDefined(response.data._issues['validator exception'])) {
                                    notify.error(gettext('Error: ' + response.data._issues['validator exception']));
                                } else {
                                    notify.error(gettext('Error: Failed to save Subscriber.'));
                                }
                            }
                        ).then(fetchSubscribers);
                };

                $scope.edit = function(subscriber) {
                    $scope.origSubscriber = subscriber || {};
                    $scope.subscriber = _.create($scope.origSubscriber);
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

    OutputChannelsDirective.$inject = ['gettext', 'notify', 'api', 'adminPublishSettingsService', 'modal'];
    function OutputChannelsDirective(gettext, notify, api, adminPublishSettingsService, modal) {
        return {
            templateUrl: 'scripts/superdesk-publish/views/output-channels.html',
            link: function ($scope) {
                $scope.outputChannel = null;
                $scope.origOutputChannel = null;
                $scope.outputChannels = null;
                $scope.subscribers = null;
                $scope.subscriberLookup = {};
                $scope.newSubscriber = {_id: null};

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

                $scope.isIncluded = function(subscriber) {
                    return $scope.outputChannel.destinations.indexOf(subscriber._id) !== -1;
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
                                if (angular.isDefined(response.data._issues) &&
                                        angular.isDefined(response.data._issues['validator exception'])) {
                                    notify.error(gettext('Error: ' + response.data._issues['validator exception']));
                                } else {
                                    notify.error(gettext('Error: Failed to save Output Channel.'));
                                }
                            }
                        ).then(fetchOutputChannels);
                };

                $scope.edit = function(outputChannel) {
                    $scope.origOutputChannel = outputChannel || {};
                    $scope.outputChannel = _.create($scope.origOutputChannel);
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
                $scope.selectorCodes = null;

                $scope.edit = function(destinationGroup) {
                    $scope.origDestinationGroup = destinationGroup || {};
                    $scope.destinationGroup = _.create($scope.origDestinationGroup);
                    $scope.selectedDestinationGroups = [];
                    $scope.selectedOutputChannels = [];
                    $scope.selectorCodes = {};
                    var destinationGroupIds = [];
                    _.each($scope.destinationGroup.destination_groups, function(item) {
                        destinationGroupIds.push(item.group);
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
                        $scope.selectorCodes[item.channel] = item.selector_codes;
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
                    $scope.selectorCodes = null;
                };

                $scope.save = function() {
                    $scope.destinationGroup.destination_groups = [];
                    _.each($scope.selectedDestinationGroups, function(group) {
                        $scope.destinationGroup.destination_groups.push({
                            group: group._id
                        });
                    });
                    $scope.destinationGroup.output_channels = [];
                    _.each($scope.selectedOutputChannels, function(channel) {
                        var outputChannel = {
                            channel: channel._id
                        };
                        if ($scope.selectorCodes[channel._id]) {
                            outputChannel.selector_codes = $scope.selectorCodes[channel._id];
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

    OutputChannelsListDirective.$inject = ['adminPublishSettingsService'];
    function OutputChannelsListDirective(adminPublishSettingsService) {
        return {
            templateUrl: 'scripts/superdesk-publish/views/output-channels-list.html',
            scope: {
                target: '=',
                selectorTarget: '=',
                exclude: '='
            },
            link: function ($scope) {
                $scope.keyword = null;
                $scope.outputChannels = null;
                $scope.parentChannel = null;
                $scope.newSelector = null;

                $scope.isSelected = function(channel) {
                    return _.findIndex($scope.target, function(selectedChannel) {
                        return channel._id === selectedChannel._id;
                    }) === -1;
                };

                $scope.addChannel = function(channel) {
                    $scope.target.push(channel);
                };

                $scope.removeChannel = function(channel) {
                    _.remove($scope.target, function(selectedChannel) {
                        return selectedChannel._id === channel._id;
                    });
                };

                $scope.addSelector = function(channel, selector) {
                    $scope.selectorTarget = $scope.selectorTarget || {};
                    $scope.selectorTarget[channel._id] = $scope.selectorTarget[channel._id] || [];
                    $scope.selectorTarget[channel._id].push(selector);
                    $scope.setParentChannel();
                };

                $scope.removeSelector = function(channel, selector) {
                    if ($scope.selectorTarget && $scope.selectorTarget[channel._id]) {
                        $scope.selectorTarget[channel._id] = _.without($scope.selectorTarget[channel._id], selector);
                    }
                };

                $scope.setParentChannel = function(channel) {
                    $scope.parentChannel = channel;
                    $scope.newSelector = null;
                };

                $scope.$watch('target', function() {
                    $scope.target = $scope.target || [];
                });

                $scope.$watch('selectorTarget', function() {
                    $scope.selectorTarget = $scope.selectorTarget || [];
                });

                $scope.$watch('keyword', _.debounce(update, 500));
                function update() {
                    $scope.outputChannels = [];
                    if ($scope.keyword) {
                        adminPublishSettingsService.fetchOutputChannelsByKeyword($scope.keyword)
                        .then(function(result) {
                            if ($scope.exclude) {
                                _.remove(result._items, function(item) {
                                    var found = false;
                                    _.each($scope.exclude, function(excludeItem) {
                                        if (excludeItem._id === item._id) {
                                            found = true;
                                            return false;
                                        }
                                    });
                                    return found;
                                });
                            }
                            $scope.outputChannels = result._items;
                        });
                    }
                }
            }
        };
    }

    DestinationGroupsListDirective.$inject = ['adminPublishSettingsService'];
    function DestinationGroupsListDirective(adminPublishSettingsService) {
        return {
            templateUrl: 'scripts/superdesk-publish/views/destination-groups-list.html',
            scope: {
                target: '=',
                exclude: '='
            },
            link: function ($scope) {
                $scope.keyword = null;
                $scope.destinationGroups = null;

                $scope.isSelected = function(group) {
                    return _.findIndex($scope.target, function(selectedGroup) {
                        return group._id === selectedGroup._id;
                    }) === -1;
                };

                $scope.addGroup = function(group) {
                    $scope.target.push(group);
                };

                $scope.removeGroup = function(group) {
                    _.remove($scope.target, function(selectedGroup) {
                        return selectedGroup._id === group._id;
                    });
                };

                $scope.$watch('target', function() {
                    $scope.target = $scope.target || [];
                });

                $scope.$watch('keyword', _.debounce(update, 500));
                function update() {
                    $scope.destinationGroups = [];
                    if ($scope.keyword) {
                        adminPublishSettingsService.fetchDestinationGroupsByKeyword($scope.keyword)
                        .then(function(result) {
                            if ($scope.exclude) {
                                _.remove(result._items, function(item) {
                                    var found = false;
                                    _.each($scope.exclude, function(excludeItem) {
                                        if (excludeItem._id === item._id) {
                                            found = true;
                                            return false;
                                        }
                                    });
                                    return found;
                                });
                            }
                            $scope.destinationGroups = result._items;
                        });
                    }
                }
            }
        };
    }

    app
        .service('adminPublishSettingsService', AdminPublishSettingsService)
        .directive('sdAdminPubSubscribers', SubscribersDirective)
        .directive('sdAdminPubOutputChannels', OutputChannelsDirective)
        .directive('sdAdminPubDestinationGroups', DestinationGroupsDirective)
        .directive('sdOutputChannelsList', OutputChannelsListDirective)
        .directive('sdDestinationGroupsList', DestinationGroupsListDirective)
        .directive('sdDestination', DestinationDirective);

    app
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/settings/publish', {
                        label: gettext('Publish'),
                        templateUrl: 'scripts/superdesk-publish/views/settings.html',
                        controller: AdminPublishSettingsController,
                        category: superdesk.MENU_SETTINGS,
                        privileges: {output_channels: 1, destination_groups: 1},
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
        }]);

    return app;
})();
