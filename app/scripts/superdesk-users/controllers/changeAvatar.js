define(['angular'], function(angular) {
    'use strict';

    function getJson(data) {
        return new Blob([angular.toJson(data)], {type: 'application/json'});
    }

    function getCords(c) {
        return {
            CropLeft: Math.round(Math.min(c.x, c.x2)),
            CropRight: Math.round(Math.max(c.x, c.x2)),
            CropTop: Math.round(Math.max(c.y, c.y2)),
            CropBottom: Math.round(Math.min(c.y, c.y2))
        };
    }

    ChangeAvatarController.$inject = ['$scope', 'upload', 'session'];
    function ChangeAvatarController($scope, upload, session) {

        $scope.methods = [
            {id: 'upload', label: gettext('Upload from computer')},
            {id: 'camera', label: gettext('Take a picture')},
            {id: 'web', label: gettext('Use a Web URL')}
        ];

        $scope.activate = function(method) {
            $scope.active = method;
            $scope.preview = {};
            $scope.progress = {width: 0};
        };

        $scope.activate($scope.methods[0]);

        $scope.upload = function(config) {
            var form = {},
                data = getCords(config.cords);

            if (config.img) {
                form.model = getJson(data);
                form.file = config.img;
            } else if (config.url) {
                data.URL = config.url;
                form.model = getJson(data);
            } else {
                return;
            }

            return upload.start({
                url: $scope.locals.data.UserAvatar.href,
                method: 'PUT',
                data: form,
                headers: {'X-Filter': 'Avatar.*'}
            }).then(function(response) {

                if ($scope.locals.data.Id === session.identity.Id) {
                    session.updateIdentity({Avatar: response.data.Avatar});
                }

                return $scope.resolve(response.data.Avatar);
            }, null, function(update) {
                $scope.progress.width = Math.round(update.loaded / update.total * 100.0);
            });
        };
    }

    return ChangeAvatarController;
});
