define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'settings', 'state', 'server', 'user',
    function UserDetailController($scope, settings, state, server, user) {
        
        $scope.initialize = function() {
            console.log(123);
        };

        $scope.initialize();
    }];
});
