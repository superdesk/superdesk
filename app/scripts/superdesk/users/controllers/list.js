define(['angular'], function(angular) {
    'use strict';

    return ['$scope', '$route', 'settings', 'server', 'users',
    function($scope, $route, settings, server, users) {

        $scope.users = users;
        $scope.settings = settings;

        $scope.delete = function(user) {
            server.delete(user).then(function() {
                $route.reload();
            });
        };

        $scope.deleteChecked = function() {
            var users = _.where($scope.users._items, {'_checked': true});
            server.deleteAll(users).then(function() {
                $route.reload();
            });
        };
    }];
});
