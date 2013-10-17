define(['angular'], function(angular) {
    'use strict';

    return ['$scope', '$location', 'server',
    function UserDetailController($scope, $location, server) {
        
        $scope.initialize = function() {
            
        };

        $scope.save = function() {
            if ($scope.user._id !== undefined) {
                server.update($scope.user).then(function() {
                    $location.path('/users/');
                    $scope.state.reload();
                });
            } else {
                server.create('users', $scope.user).then(function() {
                    $location.path('/users/');
                    $scope.state.reload();
                });
            }
        };

        $scope.initialize();
    }];
});
