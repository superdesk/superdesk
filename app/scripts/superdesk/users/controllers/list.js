define(['angular'], function(angular) {
    'use strict';

    return ['$scope', '$location', '$routeParams', 'storage', 'server', 'users', 'listDefaults',
    function($scope, $location, $routeParams, storage, server, users, listDefaults) {
        
        $scope.saveSettings = function() {
            storage.setItem('users:settings', $scope.settings, true);
        };

        $scope.loadSettings = function() {
            var settings = storage.getItem('users:settings');
            if (settings !== null) {
                $scope.settings = settings;
            } else {
                $scope.saveSettings();
            }
        };

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
        }

        //

        $scope.$watch('routeParams', function() {
            var routeParams = {};
            for (var i in $scope.routeParams) {
                if ($scope.routeParams[i] !== listDefaults[i]) {
                    routeParams[i] = $scope.routeParams[i];
                }
            }
            $location.search(routeParams);
        }, true);

        //

        $scope.users = users;

        $scope.settings = {
            fields: {
                avatar: true,
                display_name: true,
                username: false,
                email: false,
                _created: true
            }
        };
        $scope.loadSettings();

        $routeParams = angular.extend({}, listDefaults, $routeParams);
        $scope.routeParams = $routeParams;
        $scope.keyword = $routeParams.search;
    }];
});
