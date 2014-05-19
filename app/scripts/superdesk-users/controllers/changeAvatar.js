define(['angular'], function(angular) {
    'use strict';

    ChangeAvatarController.$inject = ['$scope', 'upload', 'session', 'urls'];
    function ChangeAvatarController($scope, upload, session, urls) {

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
            var form = {};
            form.CropLeft = Math.round(Math.min(config.cords.x, config.cords.x2));
            form.CropRight = Math.round(Math.max(config.cords.x, config.cords.x2));
            form.CropTop = Math.round(Math.min(config.cords.y, config.cords.y2));
            form.CropBottom = Math.round(Math.max(config.cords.y, config.cords.y2));

            if (config.img) {
                form.media = config.img;
            } else if (config.url) {
                form.URL = config.url;
            } else {
                return;
            }

            return upload.start({
                url: urls.item('/upload'),
                method: 'POST',
                data: form
            }).then(function(response) {

                if (response.data._status === 'ERR'){
                    return;
                }
                if ($scope.locals.data.Id === session.identity.Id) {
                    session.updateIdentity({upload_id: response.data._id});
                }
                $scope.locals.data.upload_id = response.data._id;
                var picture_url = 'data:' + response.data.media.content_type + ';base64,' + response.data.media.file;
                $scope.locals.data.picture_url = picture_url;

                return $scope.resolve(picture_url);
            }, null, function(update) {
                $scope.progress.width = Math.round(update.loaded / update.total * 100.0);
            });
        };
    }

    return ChangeAvatarController;
});
