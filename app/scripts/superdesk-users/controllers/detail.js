define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'upload', 'locationParams', 'server', 'notify', 'gettext',
    function ($scope, upload, locationParams, server, notify, gettext) {
        $scope.editPicture = function() {
            upload.upload('users').then(function(data) {
                $scope.user.picture_url = data._links.self.href;
                server.update($scope.user, {picture_url: $scope.user.picture_url});
            });
        };

        $scope.save = function() {
            if ('password' in $scope.user && !$scope.user.password) {
                // prevent empty password save
                delete $scope.user.password;
            }

            notify.info(gettext('Saving..'));
            if ($scope.user._id !== undefined) {
                server.update($scope.user).then(function() {
                    notify.pop();
                    notify.success(gettext('User saved.'), 3000);
                });
            } else {
                server.create('users', $scope.user).then(function(user) {
                    locationParams.path('/users/' + user._id);
                    notify.pop();
                    notify.success(gettext('User created.'), 3000);
                });
            }
        };
    }];
});
