define(['lodash'], function(_) {
    'use strict';

    UploadController.$inject = ['$scope', '$q', 'upload', 'api'];
    function UploadController($scope, $q, upload, api) {

        var promises = [];
        $scope.items = [];

        var startUpload = function(item) {
            return api.archiveMedia.getUrl().then(function(url) {
                item.upload = upload.start({
                    method: 'POST',
                    url: url,
                    data: {media: item.file},
                    headers: api.archiveMedia.getHeaders()
                }).then(function(response) {
                    item.model = response.data;
                    return item;
                }, null, function(progress) {
                    item.progress = Math.round(progress.loaded / progress.total * 100.0);
                });

                return item.upload;
            });
        };

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

                promises.push(startUpload(item));
                $scope.items.unshift(item);
            });
        };

        $scope.setAllMeta = function(field, val) {
            _.each($scope.items, function(item) {
                item.meta[field] = val;
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
            $scope.saving = true;
            return $q.all(promises)
                .then(function() {
                    return $q.all(_.map($scope.items, function(item) {
                        return api.archive.update(item.model, item.meta);
                    })).then(function(results) {
                        $scope.resolve(results);
                        return results;
                    });
                });
        };

        /**
         * Cancel uploading of single item
         *
         * @param {Object} item
         */
        function cancelItem(item) {
            if (item.model) {
                api.archive.remove(item.model);
            } else if (item.upload) {
                item.upload.abort();
            }
        }
    }

    return UploadController;
});
