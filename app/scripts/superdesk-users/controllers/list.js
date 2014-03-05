define([], function() {
    'use strict';

    UserListController.$inject = ['$scope', 'resource'];
    function UserListController($scope, resource) {

        $scope.selectedUser = null;

        resource.users.query().then(function(users) {
            $scope.users = users;
        });

        $scope.preview = function(user) {
            $scope.selectedUser = user;
        };

        $scope.closePreview = function() {
            $scope.selectedUser = null;
        };
    }

    return UserListController;
});
