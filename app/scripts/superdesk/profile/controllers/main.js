define(['angular'], function(angular) {
    'use strict';

    return ['$scope', '$rootScope', '$timeout', 'user', 'server',
    	function($scope, $rootScope, $timeout, user, server) {

             $scope.openUpload = function() {
                $scope.$emit('upload.show');
            }
                
			$scope.save = function() {
            if ('password' in $scope.user && !$scope.user.password) {
                delete $scope.user.password;
            }

            $scope.msg = 'info';
            server.update($scope.user).then(function() {
                $scope.msg = 'success';
                $timeout(function() {
                    $scope.msg = null;
                }, 3000);
            });
        };
    }];
});
