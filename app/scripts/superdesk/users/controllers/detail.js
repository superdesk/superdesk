define(['angular'], function(angular) {
    'use strict';

    return ['$scope', '$location', 'locationParams', 'server',
    function UserDetailController($scope, $location, locationParams, server) {

        $scope.initialize = function() {
            
        };

        $scope.save = function() {
            if ($scope.user._id !== undefined) {
                server.update($scope.user).then(function() {
                    locationParams.reload();
                });
            } else {
                server.create('users', $scope.user).then(function(user) {
                    locationParams.path('/users/' + user._id);
                });
            }
        };

        $scope.initialize();
    }];
});
