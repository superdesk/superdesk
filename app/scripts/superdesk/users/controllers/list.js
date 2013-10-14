define(['angular'], function(angular) {
    'use strict';

    return ['$scope', '$location', 'settings', 'state', 'server', 'users',
    function($scope, $location, settings, state, server, users) {

        $scope.users = users;
        $scope.settings = settings;
        $scope.state = state;
    }];
});
