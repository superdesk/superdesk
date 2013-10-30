define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'em', 'provider',
        function($scope, em, provider) {
            $scope.provider = provider;

            // todo(petr): maybe fetch from server?
            $scope.types = ['aap', 'reuters'];

            $scope.save = function() {
                em.save('ingest_providers', provider).then(function(result) {
                    $scope.$close(angular.extend(result, provider));
                });
            };
        }];
});
