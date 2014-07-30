define([], function() {
    'use strict';

    UserListController.$inject = ['$scope', 'server', 'superdesk', 'user'];

    function UserListController($scope, server, superdesk, user) {
        $scope.user = user;
    }

    return UserListController;
});
