define(['angular'], function(angular) {
    'use strict';

    return ['$scope', '$timeout', 'user', 'server', 'upload',
        function($scope, $timeout, user, server, upload) {
            $scope.user = user;

            $scope.openUpload = function() {
                upload.upload('users').then(function(data) {
                    $scope.user.picture_url = data._links.self.href;
                    server.update($scope.user);
                });
            };

            $scope.saveProfile = function() {
                if ('password' in $scope.user && !$scope.user.password) {
                    // prevent empty password save
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
