define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'user', function ($scope, user) {
        $scope.user = user;
    }];
});
