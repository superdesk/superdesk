define(['lodash'], function(_) {
    'use strict';

    UploadController.$inject = ['$scope', '$q', 'upload', 'api', 'archiveService'];
    function UploadController($scope, $q, upload, api, archiveService) {

        $scope.items = [];
        $scope.saving = false;
        $scope.failed = false;

        var uploadFile = function(item) {
            var handleError = function(reason) {
                item.model = false;
                $scope.failed = true;
                return $q.reject(reason);
            };

            return item.upload || api.archive.getUrl()
                .then(function(url) {
                    item.upload = upload.start({
                        method: 'POST',
                        url: url,
                        data: {media: item.file},
                        headers: api.archive.getHeaders()
                    })
                    .then(function(response) {
                        if (response.data._issues) {
                            return handleError(response);
                        }

                        item.model = response.data;
                        return item;
                    }, handleError, function(progress) {
                        item.progress = Math.round(progress.loaded / progress.total * 100.0);
                    });

                    return item.upload;
                });
        };

        var checkFail = function() {
            $scope.failed = _.some($scope.items, {model: false});
        };

        $scope.setAllMeta = function(field, val) {
            _.each($scope.items, function(item) {
                item.meta[field] = val;
            });
        };

        $scope.addFiles = function(files) {
            _.each(files, function(file) {
                var item = {
                    file: file,
                    meta: {},
                    progress: 0
                };
                item.cssType = item.file.type.split('/')[0];
                $scope.items.unshift(item);
            });
        };

        $scope.upload = function() {
            var promises = [];
            _.each($scope.items, function(item) {
                if (!item.model && !item.progress) {
                    promises.push(uploadFile(item));
                }
            });
            if (promises.length) {
                return $q.all(promises);
            }
            return $q.when();
        };

        $scope.save = function() {
            $scope.saving = true;
            return $scope.upload().then(function(results) {
                $q.all(_.map($scope.items, function(item) {
                    archiveService.addTaskToArticle(item.meta);
                    return api.archive.update(item.model, item.meta);
                })).then(function(results) {
                    $scope.resolve(results);
                });
            })
            ['finally'](function() {
                $scope.saving = false;
                checkFail();
            });
        };

        $scope.cancel = function() {
            _.each($scope.items, $scope.cancelItem, $scope);
            $scope.reject();
        };

        $scope.cancelItem = function(item, index) {
            if (item.model) {
                api.archive.remove(item.model);
            } else if (item.upload && item.upload.abort) {
                item.upload.abort();
            }
            if (index !== undefined) {
                $scope.items.splice(index, 1);
            }
            checkFail();
        };
    }

    return UploadController;
});
