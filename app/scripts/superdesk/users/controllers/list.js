define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'settings', 'server', 'locationParams', 'users', 'user',
    function UserListController($scope, settings, server, locationParams, users, user) {
        
        $scope.initialize = function() {
            $scope.users = users;
            $scope.user = user;
            $scope.settings = settings;
            $scope.locationParams = locationParams;
        };

        $scope.delete = function(user) {
            server.delete(user).then(function() {
                $route.reload();
            });
        };

        $scope.deleteChecked = function() {
            var users = _.where($scope.users._items, {'_checked': true});
            server.deleteAll(users).then(function() {
                $route.reload();
            });
        };

        $scope.initialize();
    }];
});
