define([
    'jquery',
    'angular',
    'bootstrap/modal'
], function($,angular) {
    'use strict';


    angular.module('superdesk.profile.directives.uploadavatar', [ 'blueimp.fileupload']).
        config(['fileUploadProvider', function (fileUploadProvider){
            //basic parameters overriding
            angular.extend(fileUploadProvider.defaults, {
                autoUpload : true,
                url : '//jquery-file-upload.appspot.com/',
                maxFileSize: 5000000,
                acceptFileTypes : /(\.|\/)(gif|jpe?g|png)$/i
            });

        }]).
        controller('UploaderController', ['$scope','$element', function($scope, $element){
            $scope.uploaded = false;
            $scope.preview = false;

            $scope.$on('fileuploadadd', function(e,data){
                $scope.progress = 0;
            });
            $scope.$on('fileuploadprogress', function(e, data){
                $scope.progress = data.progressInterval;
            });
            $scope.$on('fileuploaddone', function(e, data){
                console.log('upload done successfully');
                $scope.uploaded = true;
            });
            $scope.$on('fileuploadsubmit', function(e, data){
                $scope.preview = true;
                $element.find('.preview-area').append(data.files[0].preview);
            });

            
        }]).
        directive('sdUploader', function() {
            return {
                restrict: 'A',
                replace: true,
                templateUrl: 'scripts/superdesk/profile/views/uploader.html',
                controller : 'UploaderController'
            };
        }).
        directive('sdUploadPopup', function($rootScope) {
            return {
                restrict: 'A',
                replace: true,
                templateUrl: 'scripts/superdesk/profile/views/upload-popup.html',
                link: function(scope, element, attrs) {

                    function showmodal() {
                        $(element).modal('show');
                    }

                    scope.close = function() {
                        $(element).modal('hide');
                    }

                    scope.save = function() {
                        //do saving
                        scope.close();
                    }

                    $rootScope.$on('upload.show', showmodal);
                }
            };
        });
});
