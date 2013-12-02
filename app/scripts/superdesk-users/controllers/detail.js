define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'upload', 'locationParams', 'em', 'notify', 'gettext',
    function ($scope, upload, locationParams, em, notify, gettext) {

        em.repository('user_roles').all().then(function(roles) {
            $scope.userRoles = roles._items;
        });

        $scope.editPicture = function() {
            upload.upload('users').then(function(data) {
                $scope.user.picture_url = data.url;
                em.update($scope.user, {picture_url: $scope.user.picture_url});
            });
        };

        $scope.save = function() {
            if ('password' in $scope.user && !$scope.user.password) {
                // prevent empty password save
                delete $scope.user.password;
            }

            notify.info(gettext('Saving..'));
            if ($scope.user._id !== undefined) {
                em.update($scope.user).then(function() {
                    notify.pop();
                    notify.success(gettext('User saved.'), 3000);
                });
            } else {
                em.create('users', $scope.user).then(function(user) {
                    locationParams.path('/users/' + user._id);
                    notify.pop();
                    notify.success(gettext('User created.'), 3000);
                });
            }
        };
    }];
});
