define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    return ['$scope', 'providerTypes', 'providerRepository', 'em', 'gettext', 'notify',
        function($scope, providerTypes, providerRepository, em, gettext, notify) {

            var _provider = null;
            $scope.provider = null;
            $scope.types = providerTypes;

            providerRepository.findAll().then(function(providers) {
                $scope.providers = providers;
            });

            $scope.remove = function(provider) {
                em.remove(provider).then(function() {
                    _.remove($scope.providers._items, provider);
                    notify.success(gettext('Provider deleted.'), 3000);
                });
            };

            $scope.edit = function(provider) {
                $scope.provider = angular.extend({}, provider);
                _provider = provider;
            };

            $scope.cancel = function() {
                $scope.provider = null;
            };

            $scope.save = function(provider) {
                em.save('ingest_providers', provider).then(function(result) {
                    $scope.cancel();
                    angular.extend(provider, result);
                    notify.success(gettext('Provider saved!'), 3000);
                    if (!_provider) {
                        $scope.providers._items.unshift(provider);
                    } else {
                        angular.extend(_provider, provider);
                    }
                });
            };
        }];
});
