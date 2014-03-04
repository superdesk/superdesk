define([], function() {
    'use strict';

    return ['$scope', 'user', function ($scope, user) {
        $scope.user = user;
    }];
});
