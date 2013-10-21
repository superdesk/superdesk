define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'settings', 'server', 'locationParams', 'users', 'user',
    function UserListController($scope, settings, server, locationParams, users, user) {
        
        $scope.initialize = function() {
            $scope.users = users;
            $scope.user = user;
            $scope.settings = settings;
            $scope.locationParams = locationParams;
            $scope.search = locationParams.get('search');
        };

        $scope.delete = function(user) {
            server.delete(user).then(function() {
                locationParams.reload();
            });
        };

        $scope.deleteChecked = function() {
            var users = _.where($scope.users._items, {'_checked': true});
            server.deleteAll(users).then(function() {
                locationParams.reload();
            });
        };

        $scope.initialize();

    }];
});
