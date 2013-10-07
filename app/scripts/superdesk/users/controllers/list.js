define(['angular'], function(angular) {
    'use strict';

    return ['$scope', '$location', '$routeParams', 'settings', 'server', 'users', 'defaultListParams', 'defaultSettings',
    function($scope, $location, $routeParams, settings, server, users, defaultListParams, defaultSettings) {
        
        $scope.search = function() {
            $scope.routeParams.search = $scope.keyword;
        };

        $scope.sort = function(field) {
            if ($scope.routeParams.sortField === field) {
                if ($scope.routeParams.sortDirection === 'asc') {
                    $scope.routeParams.sortDirection = 'desc';
                } else {
                    $scope.routeParams.sortDirection = 'asc';
                }
            } else {
                $scope.routeParams.sortField = field;
                $scope.routeParams.sortDirection = 'asc';
            }
        };

        //

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
        $scope.keyword = $routeParams.search;
    }];
});
