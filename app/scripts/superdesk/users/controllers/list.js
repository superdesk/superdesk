define(['angular'], function(angular) {
    'use strict';

    return ['$scope', '$location', 'users',
    function($scope, $location, users) {
        $scope.users = users;
        console.log(users);

        /*
        $scope.open = function(path) {
            $location.path(path);
        };

        $scope.edit = function(item) {
            $scope.editItem = item;
        };

        $scope.closeEdit = function() {
            $scope.editItem = null;
        };
        */
    }];
});
