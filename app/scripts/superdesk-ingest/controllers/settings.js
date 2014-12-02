define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    return ['$scope', 'providerTypes', 'gettext', 'notify', 'api', '$location',
        function($scope, providerTypes, gettext, notify, api, $location) {

            $scope.origProvider = null;
            $scope.provider = null;
            $scope.types = providerTypes;

            api.ingestProviders.query({max_results: 1000})
            .then(function(result) {
                $scope.providers = result;
            });

            $scope.remove = function(provider) {
                api.ingestProviders.remove(provider)
                .then(function(result) {
                    _.remove($scope.providers._items, provider);
                    notify.success(gettext('Provider deleted.'), 3000);
                });
            };

            $scope.edit = function(provider) {
                $scope.origProvider = provider || {};
                $scope.provider = _.create(provider);
            };

            $scope.cancel = function() {
                $scope.origProvider = null;
                $scope.provider = null;
            };

            $scope.setConfig = function(provider) {
                $scope.provider.config = provider.config;
            };

            $scope.save = function() {
                api.ingestProviders.save($scope.origProvider, $scope.provider)
                .then(function(result) {
                    notify.success(gettext('Provider saved!'), 3000);
                    if (!$scope.provider._id) {
                        $scope.providers._items.unshift($scope.origProvider);
                    }
                    $scope.cancel();
                });
            };

            $scope.gotoIngest = function(source) {
                $location.path('/workspace/ingest').search('source', angular.toJson([source]));
            };
        }];
});
