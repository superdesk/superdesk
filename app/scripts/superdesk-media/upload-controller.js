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
                    return api.image.getUrl().then(function(url) {
                        item.upload = $upload.upload({
                            method: 'POST',
                            url: url,
                            file: file,
                            isUpload: true,
                            headers: api.image.getHeaders()
                        }).then(function(response) {
                            item.model = response.data;
                            return item;
                        }, null, function(progress) {
                            item.progress = Math.round(progress.loaded / progress.total * 100.0);
                        });

                        return item.upload;
                    });
                };

                promises.push(upload());
                $scope.items.unshift(item);
            });
        };

        $scope.cancel = function() {
            _.each($scope.items, cancelItem);
            $scope.reject();
        };

        $scope.cancelOne = function(item, index) {
            cancelItem(item);
            $scope.items.splice(index, 1);
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

        /**
         * Cancel uploading of single item
         *
         * @param {Object} item
         */
        function cancelItem(item) {
            if (item.model) {
                api.image.remove(item.model);
            } else if (item.upload) {
                item.upload.abort();
            }
        }
    }

    return UploadController;
});
