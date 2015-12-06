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

    var app = angular.module('superdesk.searchProviders', ['superdesk.activity']);

    app.value('providerTypes', {
        aapmm: 'AAP Multimedia'
    });

    SearchProviderService.$inject = ['providerTypes'];
    function SearchProviderService(providerTypes) {
        var service = {
            getProviderTypes: function () {
                return providerTypes;
            }
        };

        return service;
    }

    SearchProviderSettingsController.$inject = ['$scope', 'privileges'];
    /**
     * Controller for the Search Provider Settings.
     */
    function SearchProviderSettingsController($scope, privileges) {
    }

    SearchProviderConfigDirective.$inject = ['providerTypes', 'gettext', 'notify', 'api', '$filter', 'modal'];
    function SearchProviderConfigDirective(providerTypes, gettext, notify, api, $filter, modal) {
        return {
            templateUrl: 'scripts/superdesk-search-providers/views/search-provider-config.html',
            link: function ($scope) {
                $scope.provider = null;
                $scope.origProvider = null;
                $scope.providers = null;
                $scope.newDestination = null;
                $scope.providerTypes = providerTypes;

                /**
                 * Fetches all search providers from backend
                 */
                function fetchSearchProviders() {
                    api.search_providers.query({}).then(
                        function(result) {
                            $scope.providers = $filter('sortByName')(result._items, 'search_provider');
                        }
                    );
                }

                /**
                 * Upserts the selected search provider.
                 */
                $scope.save = function() {
                    api.search_providers.save($scope.origProvider, $scope.provider)
                        .then(
                            function() {
                                notify.success(gettext('Search Provider saved.'));
                                $scope.cancel();
                            },
                            function(response) {
                                if (angular.isDefined(response.data._issues)) {
                                    if (angular.isDefined(response.data._issues['validator exception'])) {
                                        notify.error(gettext('Error: ' + response.data._issues['validator exception']));
                                    } else if (angular.isDefined(response.data._issues.search_provider) &&
                                        angular.isDefined(response.data._issues.search_provider.unique)) {
                                        notify.error(gettext('Error: A Search Provider with type ' +
                                            $scope.providerTypes[$scope.provider.search_provider] + ' already exists.'));
                                    }
                                } else {
                                    notify.error(gettext('Error: Failed to save Search Provider.'));
                                }
                            }
                        ).then(fetchSearchProviders);
                };

                /**
                 * Either initializes a new provider object for adding a new provider or initializes the provider object
                 * with the selected provider allowing user to update the provider details.
                 */
                $scope.edit = function(provider) {
                    $scope.origProvider = provider || {};
                    $scope.provider = _.create($scope.origProvider);
                };

                /**
                 * Removes the selected search provider.
                 */
                $scope.remove = function(provider) {
                    modal.confirm(gettext('Are you sure you want to delete Search Provider?')).then(
                        function removeSearchProvider() {
                            api.search_providers.remove(provider)
                                .then(
                                    function () {
                                        notify.success(gettext('Search Provider deleted.'));
                                    },
                                    function(response) {
                                        if (angular.isDefined(response.data._message)) {
                                            notify.error(response.data._message);
                                        } else {
                                            notify.error(gettext('Error: Unable to delete Search Provider.'));
                                        }
                                    }
                                ).then(fetchSearchProviders);
                        }
                    );
                };

                /**
                 * Reverts any changes made to the provider
                 */
                $scope.cancel = function() {
                    $scope.origProvider = null;
                    $scope.provider = null;
                };

                fetchSearchProviders();
            }
        };
    }

    app
        .directive('sdSearchProviderConfig', SearchProviderConfigDirective)
        .service('searchProviderService', SearchProviderService)
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/settings/searchProviders', {
                    label: gettext('Search Providers'),
                    templateUrl: 'scripts/superdesk-search-providers/views/settings.html',
                    controller: SearchProviderSettingsController,
                    category: superdesk.MENU_SETTINGS,
                    privileges: {search_providers: 1},
                    priority: 2000
                });
        }])
        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('search_providers', {
                type: 'http',
                backend: {
                    rel: 'search_providers'
                }
            });
        }]);

    return app;
})();
