define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'server', 'locationParams', 'superdesk', 'roles',
    function UserListController($scope, server, locationParams, superdesk, roles) {

        $scope.selectedUser = null;
        $scope.roles = roles;

        $scope.users = superdesk.data('users', {
            sort: ['display_name', 'asc'],
            perPage: 25
        });

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

        $scope.createUser = function() {
            $scope.selectedUser = {};
        };

        $scope.preview = function(user) {
            $scope.selectedUser = user;
        };

        $scope.closePreview = function() {
            $scope.selectedUser = null;
        };

    }];
});
