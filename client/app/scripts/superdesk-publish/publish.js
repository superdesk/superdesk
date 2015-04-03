(function() {
    'use strict';

    var app = angular.module('superdesk.publish', ['superdesk.users']);

    AdminPublishSettingsController.$inject = ['$scope', 'privileges'];
    function AdminPublishSettingsController($scope, privileges) {
        var user_privileges = privileges.privileges;

        $scope.showOutputChannels   = Boolean(user_privileges.output_channels);
        $scope.showDestinationGroups  = Boolean(user_privileges.destination_groups);
    }

    AdminPublishSettingsService.$inject = ['api', '$q'];
    function AdminPublishSettingsService(api, $q) {

        var service = {
            fetchOutputChannels: function() {
                return api.output_channels.query({max_results: 200});
            },

            fetchDestinationGroups: function() {
                return api.destination_groups.query({max_results: 200});
            }
        };

        return service;
    }

    OutputChannelsDirective.$inject = ['gettext', 'notify', 'api', 'adminPublishSettingsService', 'modal'];
    function OutputChannelsDirective(gettext, notify, api, adminPublishSettingsService, modal) {
        return {
            templateUrl: 'scripts/superdesk-publish/views/output-channels.html',
            link: function ($scope) {
                $scope.outputChannel = null;
                $scope.origOutputChannel = null;

                function fetchOutputChannels() {
                    adminPublishSettingsService.fetchOutputChannels().then(
                        function(result) {
                            $scope.outputChannels = result;
                        }
                    );
                }

                function confirm() {
                    return modal.confirm(gettext('Are you sure you want to delete output channel?'));
                }

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
                    confirm().then(function() {
                        api.output_channels.remove(outputChannel)
                        .then(function(result) {
                            _.remove($scope.outputChannels, outputChannel);
                        }, function(response) {
                            if (angular.isDefined(response.data._message)) {
                                notify.error(gettext('Error: ' + response.data._message));
                            } else {
                                notify.error(gettext('There is an error. Output Channel cannot be deleted.'));
                            }
                        }).then(fetchOutputChannels);
                    });
                };

                $scope.cancel = function() {
                    $scope.origOutputChannel = null;
                    $scope.outputChannel = null;
                };

                fetchOutputChannels();
            }
        };
    }

    DestinationGroupsDirective.$inject = ['gettext', 'notify', 'api', 'adminPublishSettingsService', 'modal'];
    function DestinationGroupsDirective(gettext, notify, api, adminPublishSettingsService, modal) {
        return {
            templateUrl: 'scripts/superdesk-publish/views/destination-groups.html',
            link: function ($scope) {
                $scope.destinationGroup = null;
                $scope.origDestinationGroup = null;

                function fetchDestinationGroups() {
                    adminPublishSettingsService.fetchDestinationGroups().then(
                        function(result) {
                            $scope.destinationGroups = result;
                        }
                    );
                }

                function confirm() {
                    return modal.confirm(gettext('Are you sure you want to delete destination group?'));
                }

                $scope.save = function() {
                    api.destination_groups.save($scope.origDestinationGroup, $scope.destinationGroup)
                        .then(
                            function() {
                                notify.success(gettext('Destination Group saved.'));
                                $scope.cancel();
                            },
                            function(response) {
                                if (angular.isDefined(response.data._issues) &&
                                        angular.isDefined(response.data._issues['validator exception'])) {
                                    notify.error(gettext('Error: ' + response.data._issues['validator exception']));
                                } else {
                                    notify.error(gettext('Error: Failed to save Destination Group.'));
                                }
                            }
                        ).then(fetchDestinationGroups);
                };

                $scope.edit = function(destinationGroup) {
                    $scope.origDestinationGroup = destinationGroup || {};
                    $scope.destinationGroup = _.create($scope.origDestinationGroup);

                    adminPublishSettingsService.fetchOutputChannels().then(function(result) {
                        if (angular.isDefined(result) && angular.isDefined(result._items)) {
                            $scope.outputChannels = result._items;
                        }
                    });

                    adminPublishSettingsService.fetchDestinationGroups().then(function(result) {
                        if (angular.isDefined(result) && angular.isDefined(result._items)) {
                            $scope.destinationGroupsLookup = result._items;
                        }
                    });
                };

                $scope.remove = function(destinationGroup) {
                    confirm().then(function() {
                        api.destination_groups.remove(destinationGroup)
                        .then(function(result) {
                            _.remove($scope.destinationGroups, destinationGroup);
                        }, function(response) {
                            if (angular.isDefined(response.data._message)) {
                                notify.error(gettext('Error: ' + response.data._message));
                            } else {
                                notify.error(gettext('There is an error. Destination Group cannot be deleted.'));
                            }
                        }).then(fetchDestinationGroups);
                    });
                };

                $scope.cancel = function() {
                    $scope.origDestinationGroup = null;
                    $scope.destinationGroup = null;
                };

                fetchDestinationGroups();
            }
        };
    }

    app
        .service('adminPublishSettingsService', AdminPublishSettingsService)
        .directive('sdAdminPubOutputChannels', OutputChannelsDirective)
        .directive('sdAdminPubDestinationGroups', DestinationGroupsDirective);

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
        }]);

    return app;
})();
