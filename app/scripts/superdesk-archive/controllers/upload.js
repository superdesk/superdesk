define(['lodash'], function(_) {
    'use strict';

    UploadController.$inject = ['$scope', '$q', 'upload', 'api'];
    function UploadController($scope, $q, upload, api) {

        $scope.items = [];
        $scope.saving = false;
        $scope.failed = false;

        var uploadFile = function(item) {
            return api.archiveMedia.getUrl()
                .then(function(url) {
                    var x;
                    if (Math.random() > 0.50) {
                        x = upload;
                    } else {
                        x = {
                            start: function() {
                                var p = $q.defer();
                                p.reject();
                                return p.promise;
                            },
                            abort: function() {}
                        };
                    }
                    item.upload = x.start({
                    //item.upload = upload.start({
                        method: 'POST',
                        url: url,
                        data: {media: item.file},
                        headers: api.archiveMedia.getHeaders()
                    })
                    .then(function(response) {
                        item.model = response.data;
                        return item;
                    }, function(response) {
                        item.model = false;
                        return $q.reject();
                    }, function(progress) {
                        item.progress = Math.round(progress.loaded / progress.total * 100.0);
                    })
                    .finally(function() {
                        checkFail();
                    });
                    return item.upload;
                });
        };

        var checkFail = function() {
            $scope.failed = false;
            _.each($scope.items, function(item) {
                if (item.model === false) {
                    $scope.failed = true;
                    return false;
                }
            });
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
                $scope.items.unshift(item);
            });
            $scope.upload();
        };

        $scope.upload = function() {
            var promises = [];
            _.each($scope.items, function(item) {
                if (!item.model) {
                    promises.push(uploadFile(item));
                }
            });
            if (promises.length) {
                return $q.all(promises);
            }
            return $q.resolve();
        };

        $scope.save = function() {
            $scope.saving = true;
            $scope.upload().then(function(results) {
                $q.all(_.map($scope.items, function(item) {
                    return api.archive.update(item.model, item.meta);
                })).then(function(results) {
                    $scope.resolve(results);
                });
            })
            .finally(function() {
                $scope.saving = false;
                checkFail();
            });
        };

        $scope.cancel = function() {
            _.each($scope.items, function(item) {
                $scope.cancelItem(item);
            });
            $scope.reject();
        };

        $scope.cancelItem = function(item, index) {
            if (item.model) {
                api.archive.remove(item.model);
            } else if (item.upload) {
                //item.upload.abort();
            }
            if (index !== undefined) {
                $scope.items.splice(index, 1);
            }
            checkFail();
        };
    }

    return UploadController;
});
