define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'settings', 'state', 'server', 'users',
    function($scope, settings, state, server, users) {

        $scope.users = users;
        $scope.settings = settings;
        $scope.state = state;

        $scope.delete = function(user) {
            server.delete(user).then(function() {
                state.reload();
            });
        };

        $scope.deleteChecked = function() {
            var users = _.where($scope.users._items, {'_checked': true});
            server.deleteAll(users).then(function() {
                state.reload();
            });
        };
    }];
});
