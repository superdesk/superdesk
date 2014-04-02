define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk')
        .service('upload', ['$q', '$rootScope', function($q, $rootScope) {
            function UploadService() {/**
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
        }])
        .directive('sdUploadModal', ['upload', function(upload) {
            return {
                restrict: 'A',
                replace: true,
                templateUrl: 'scripts/superdesk/views/upload.html',
                scope: {},
                link: function(scope, element, attrs) {
                    var result;
                    scope.open = false;

                    scope.close = function() {
                        upload.delay.reject();
                        scope.open = false;
                    };

                    scope.save = function() {
                        scope.open = false;
                        if (result) {
                            upload.delay.resolve(result);
                        } else {
                            upload.delay.reject();
                        }
                    };

                    scope.$on('fileuploadadd', function(e, data) {
                        scope.progress = 0;
                    });

                    scope.$on('fileuploadprogress', function(e, data) {
                        scope.progress = data.progressInterval;
                    });

                    scope.$on('fileuploaddone', function(e, data) {
                        scope.uploaded = true;
                        result = data.result;
                    });

                    scope.$on('fileuploadsubmit', function(e, data) {
                        scope.preview = true;
                        element.find('.preview-area').empty().append(data.files[0].preview);
                    });

                    scope.$on('upload:show', function() {
                        result = null;
                        scope.progress = 0;
                        scope.preview = false;
                        scope.uploaded = false;
                        scope.open = true;
                    });
                }
            };
        }]);
});
