define(['lodash'], function(_) {
    'use strict';

    UploadController.$inject = ['$scope', '$upload', '$q', 'api'];
    function UploadController($scope, $upload, $q, api) {

        var promises = [];
        $scope.items = [];

        /**
         * Add files
         *
         * @param {Collection} files
         */
        $scope.addFiles = function(files) {
            _.each(files, function(file) {
                var item = {
                    file: file,
                    meta: {},
                    progress: 0
                };

                var upload = function() {
                    return api.media.getUrl().then(function(url) {
                        return $upload.upload({
                            method: 'POST',
                            url: url,
                            file: file
                        }).then(function(response) {
                            item.model = response.data;
                            return item;
                        }, null, function(progress) {
                            item.progress = Math.round(progress.loaded / progress.total * 100.0);
                        });
                    });
                };

                promises.push(upload());
                $scope.items.unshift(item);
            });
        };

        $scope.remove = function(file) {
            $scope.items = _.without($scope.items, file);
        };

        /**
         * Wait for uploads to finish and save meta
         */
        $scope.save = function() {
            return $q.all(promises)
                .then(function() {
                    return $scope.items;
                });
        };
    }

    return UploadController;
});
