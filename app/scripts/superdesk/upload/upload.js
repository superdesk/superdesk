define([
    'angular',
    'require',
    './upload-service',
    './image-preview-directive',
    './video-capture-directive',
    './crop-directive',
    './upload-modal-directive'
], function(angular, require) {
    'use strict';

    return angular.module('superdesk.upload', [])
        .service('upload', require('./upload-service'))
        .directive('sdImagePreview', require('./image-preview-directive'))
        .directive('sdVideoCapture', require('./video-capture-directive'))
        .directive('sdCrop', require('./crop-directive'))
        .directive('sdUploadModal', require('./upload-modal-directive'));
});
