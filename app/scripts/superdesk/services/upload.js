define([
    'jquery',
    'angular',
    'bootstrap/modal',
    'file-upload/jquery.fileupload-angular',
], function($, angular) {
    'use strict';

    angular.module('superdesk.services.upload', ['blueimp.fileupload'])
        .config(['fileUploadProvider', function(fileUploadProvider){
            angular.extend(fileUploadProvider.defaults, {
                autoUpload: true,
                url: ServerConfig.url + '/upload',
                maxFileSize: 5000000,
                acceptFileTypes: /(\.|\/)(gif|jpe?g|png)$/i
            });
        }])
        .service('upload', function($q, $rootScope) {
            function UploadService() {
                /**
                 * Start upload workflow
                 *
                 * @param {string} base
                 * @return {object} promise
                 */
                this.upload = function(base) {
                    this.delay = $q.defer();
                    $rootScope.$broadcast('upload:show');
                    return this.delay.promise;
                };
            }

            return new UploadService();
        })
        .directive('sdUploadModal', ['upload', function(upload) {
            return {
                restrict: 'A',
                replace: true,
                templateUrl: 'scripts/superdesk/views/upload.html',
                scope: {},
                link: function(scope, element, attrs) {
                    var result;

                    scope.close = function() {
                        $(element).modal('hide');
                        upload.delay.reject();
                    };

                    scope.save = function() {
                        scope.close();
                        upload.delay.resolve(result);
                    };

                    scope.$on('fileuploadadd', function(e,data) {
                        scope.progress = 0;
                    });

                    scope.$on('fileuploadprogress', function(e, data){
                        scope.progress = data.progressInterval;
                    });

                    scope.$on('fileuploaddone', function(e, data){
                        scope.uploaded = true;
                        result = data.result;
                    });

                    scope.$on('fileuploadsubmit', function(e, data){
                        scope.preview = true;
                        element.find('.preview-area').empty().append(data.files[0].preview);
                    });

                    scope.$on('upload:show', function() {
                        result = null;
                        scope.progress = 0;
                        scope.preview = false;
                        scope.uploaded = false;
                        $(element).modal('show');
                    });
                }
            };
        }]);
});
