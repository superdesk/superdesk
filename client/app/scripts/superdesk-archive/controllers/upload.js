define(['lodash'], function(_) {
    'use strict';

    UploadController.$inject = ['$scope', '$q', 'upload', 'api', 'archiveService', 'session'];
    function UploadController($scope, $q, upload, api, archiveService, session) {

        $scope.items = [];
        $scope.saving = false;
        $scope.failed = false;
        $scope.enableSave = false;
        $scope.currentUser =  session.identity;

        var requiredFields = ['headline', 'description', 'slugline'];

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

        var validateFields = function () {
            $scope.errorMessage = null;
            if (!_.isEmpty($scope.items)) {
                _.each($scope.items, function(item) {
                    _.each(requiredFields, function(key) {
                        if (item.meta[key] == null || _.isEmpty(item.meta[key])) {
                            $scope.errorMessage = 'Required field(s) are missing';
                            return false;
                        }
                    });
                });
            }
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
                    meta: {byline: $scope.currentUser.byline},  // initialize meta.byline from user profile
                    progress: 0
                };
                item.cssType = item.file.type.split('/')[0];
                $scope.items.unshift(item);
                $scope.enableSave = true;
            });
        };

        $scope.upload = function() {
            var promises = [];
            _.each($scope.items, function(item) {
                if (!item.model && !item.progress) {
                    item.upload = null;
                    promises.push(uploadFile(item));
                }
            });
            if (promises.length) {
                return $q.all(promises);
            }
            return $q.when();
        };

        $scope.save = function() {
            validateFields();
            if ($scope.errorMessage == null) {
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
            }
        };

        $scope.cancel = function() {
            _.each($scope.items, $scope.cancelItem, $scope);
            $scope.reject();
        };

        $scope.tryAgain = function() {
            $scope.failed = null;
            $scope.upload();
        };

        $scope.cancelItem = function(item, index) {
            if (item != null) {
                if (item.model) {
                    api.archive.remove(item.model);
                } else if (item.upload && item.upload.abort) {
                    item.upload.abort();
                }
            }
            if (index !== undefined) {
                $scope.items.splice(index, 1);
            }
            if (_.isEmpty($scope.items)) {
                $scope.enableSave = false;
            }
            checkFail();
        };
    }

    return UploadController;
});
