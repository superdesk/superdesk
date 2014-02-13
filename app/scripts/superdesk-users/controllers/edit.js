define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'server', 'superdesk', 'roles', 'user',
    function UserListController($scope, server, superdesk, roles, user) {

        $scope.user = user;
        $scope.roles = roles;

    }];
});
