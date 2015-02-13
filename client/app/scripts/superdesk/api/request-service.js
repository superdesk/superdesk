define([], function() {
    'use strict';

    /**
     * Service for re-sending requests
     */
    RequestService.$inject = ['$injector'];
    function RequestService($injector) { // using $injector to avoid circular dependency on $http

        /**
         * @link upload:isUpload
         */
        this.isUpload = function(config) {
            return $injector.get('upload').isUpload(config);
        };

        /**
         * Request again using given config
         *
         * @param {Object} config
         * @returns {Promise}
         */
        this.resend = function(config) {
            return this.isUpload(config) ? $injector.get('upload').restart(config) : $injector.get('$http')(config);
        };
    }

    return RequestService;
});
