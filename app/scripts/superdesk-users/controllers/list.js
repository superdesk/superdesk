define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'userSettings', 'server', 'locationParams', 'users', 'roles', 'user',
    function UserListController($scope, userSettings, server, locationParams, users, roles, user) {
        $scope.user = user;
        $scope.users = users;
        $scope.roles = roles;

        $scope.userSettings = userSettings;
        $scope.locationParams = locationParams;
        $scope.search = locationParams.get('search');

        $scope['delete'] = function(user) {
            server['delete'](user).then(function() {
                locationParams.reload();
            });
        };

        $scope.deleteChecked = function() {
            var users = _.where($scope.users._items, {'_checked': true});
            server.deleteAll(users).then(function() {
                locationParams.reload();
            });
        };

        $scope.edit = function(user) {
            locationParams.path('/users/' + user._id);
        };
    }];
});
