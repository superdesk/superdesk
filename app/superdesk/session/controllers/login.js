define(['angular'], function(angular) {
    'use strict';
    
    var LoginController = function($scope, authService) {
        $scope.activate = function() {
            $('#loginModal').modal();
        };
        $scope.deactivate = function() {
            $('#loginModal').modal('hide');
        };

        //
        if (!authService.getToken()) {
            $scope.activate();
        }
    };

    return LoginController;
});
