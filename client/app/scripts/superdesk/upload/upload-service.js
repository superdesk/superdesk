define([], function() {
    'use strict';

    UploadService.$inject = ['$q', '$upload'];
    function UploadService($q, $upload) {
        /**
         * Start upload
         *
         * @param {Object} config
         * @returns Promise
         */
        this.start = function(config) {
            config.isUpload = true;
            return $upload.upload(config);
        };

        /**
         * Restart upload
         *
         * @param {Object} config
         * @returns {Promise}
         */
        this.restart = function(config) {
            return $upload.http(config);
        };

        /**
         * Test if given request config is an upload
         *
         * @param {Object} config
         * @returns {bool}
         */
        this.isUpload = function(config) {
            return config.isUpload || false;
        };
    }

    return UploadService;
});
