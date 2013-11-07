define(['lodash'], function(_) {
    'use strict';

    return ['$scope', '$routeParams', '$location', 'providerRepository',
    function($scope, $routeParams, $location, providerRepository) {

        providerRepository.findAll().then(function(providers) {
            $scope.providers = providers;
            if ('provider' in $routeParams) {
                $scope.activeProvider = _.find(providers._items, {_id: $routeParams.provider});
            }

            $scope.set_provider = function(provider_id) {
                $location.search('provider', provider_id);
            };
        });
    }];
});