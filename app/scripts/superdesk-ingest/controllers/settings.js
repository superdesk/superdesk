define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    return ['$scope', 'providerTypes', 'gettext', 'notify', 'api', '$location',
        function($scope, providerTypes, gettext, notify, api, $location) {

            var DEFAULT_SCHEDULE = {minutes: 5, seconds: 0};

            $scope.provider = null;
            $scope.origProvider = null;

            $scope.types = providerTypes;
            $scope.minutes = [0, 1, 2, 3, 4, 5, 8, 10, 15, 30, 45];
            $scope.seconds = [0, 5, 10, 15, 30, 45];

            fetchProviders();

            function fetchProviders() {
                return api.ingestProviders.query({max_results: 100})
                    .then(function(result) {
                        $scope.providers = result;
                    });
            }

            $scope.remove = function(provider) {
                api.ingestProviders.remove(provider)
                .then(function() {
                    notify.success(gettext('Provider deleted.'));
                }).then(fetchProviders);
            };

            $scope.edit = function(provider) {
                $scope.origProvider = provider || {};
                $scope.provider = _.create($scope.origProvider);
                $scope.provider.update_schedule = $scope.origProvider.update_schedule || DEFAULT_SCHEDULE;
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
                .then(function() {
                    notify.success(gettext('Provider saved!'));
                    $scope.cancel();
                }).then(fetchProviders);
            };

            $scope.gotoIngest = function(source) {
                $location.path('/workspace/ingest').search('source', angular.toJson([source]));
            };
        }];
});
