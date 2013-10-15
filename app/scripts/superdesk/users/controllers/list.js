define(['angular'], function(angular) {
    'use strict';

    return ['$scope', '$location', '$routeParams', 'settings', 'state', 'server', 'users', 'defaultListParams',
    function($scope, $location, $routeParams, settings, state, server, users, defaultListParams) {
        
        $scope.$watch('routeParams', function() {
            var routeParams = {};
            for (var i in $scope.routeParams) {
                if ($scope.routeParams[i] !== defaultListParams[i]) {
                    routeParams[i] = $scope.routeParams[i];
                }
            }
            $location.search(routeParams);
        }, true);

        //

        $scope.users = users;
        $scope.settings = settings;
        $scope.state = state;

        $routeParams = angular.extend({}, defaultListParams, $routeParams);
        $scope.routeParams = $routeParams;
    }];
});
