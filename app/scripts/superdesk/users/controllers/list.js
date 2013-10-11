define(['angular'], function(angular) {
    'use strict';

    return ['$scope', '$location', '$routeParams', 'settings', 'server', 'users', 'defaultListParams', 'defaultSettings',
    function($scope, $location, $routeParams, settings, server, users, defaultListParams, defaultSettings) {
        
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

        $scope.settings = settings.initialize('users', defaultSettings);
        $scope.settings.load();

        $routeParams = angular.extend({}, defaultListParams, $routeParams);
        $scope.routeParams = $routeParams;
    }];
});
