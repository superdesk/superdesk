define(['lodash'], function(_) {
    'use strict';

    UserListController.$inject = ['$scope', 'resource'];
    function UserListController($scope, resource) {

        $scope.selectedUser = null;
        $scope.createdUsers = [];

        resource.users.query({desc: 'createdOn'}).then(function(users) {
            $scope.users = users;
        });

        $scope.preview = function(user) {
            $scope.selectedUser = user;
        };

        $scope.createUser = function() {
            $scope.preview({});
        };

        $scope.closePreview = function() {
            $scope.preview(null);
        };

        // make sure saved user is presented in the list
        $scope.render = function(user) {
            if (_.find($scope.users._items, {href: user.href})) {
                return;
            }

            if (_.find($scope.createdUsers, {href: user.href})) {
                return;
            }

            $scope.createdUsers.unshift(user);
        };
    }

    return UserListController;
});
