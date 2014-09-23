define([], function() {
    'use strict';

    UserListController.$inject = ['$scope', 'server', 'superdesk', 'user', 'session'];

    function UserListController($scope, server, superdesk, user, session) {
        $scope.user = user;

        $scope.profile = $scope.user._id === session.identity._id;
    }

    return UserListController;
});
